import asyncio
import json
from typing import Dict, List, Optional, Any, TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from agent import MyAgentState
from rag import create_rag_tool
from rag.llm_config import get_llm
from score import get_student_scores, get_student_info, calculate_average_scores

load_dotenv()


def create_supervisor_agent(model_name: str = "gpt-3.5-turbo"):
    """Create a Supervisor Agent with ReAct capabilities"""

    # Define tools
    score_tool = get_student_scores
    student_info_tool = get_student_info
    rag_tool = create_rag_tool()
    calculator_tool = calculate_average_scores

    # Get all tools
    tools = [score_tool, student_info_tool, calculator_tool, rag_tool]

    # System prompt
    system_prompt = """You are a helpful AI assistant for KMA (Academy of Cryptography Techniques) students.
    Your job is to help students with their questions about KMA regulations, their information, and their scores.
    
    You have access to the following tools:
    - search_kma_regulations: Search for information in KMA's regulations, rules, and policies - USE THIS TOOL FIRST for any questions about KMA rules, requirements, policies, or procedures
    - get_student_scores: Get student's scores with filtering options (semester must be in format ki1-2024-2025, k2-2024-2025, etc.)
    - get_student_info: Get student's information (name, class)
    - calculate_average_scores: Calculate average scores for a student
    
    Follow a step-by-step process:
    1. Understand the student's question
    2. Decide which tool(s) to use:
       - For questions about regulations, requirements, or policies, use search_kma_regulations
       - For questions about a student's scores, use get_student_info followed by get_student_scores
       - For questions about averages or GPAs, use calculate_average_scores after getting scores
    3. If you need student information that isn't provided, ask the student for it
    4. Use the appropriate tool(s) to get the information
    5. Process the information if needed
    6. Respond to the student in a helpful, clear way
    
    When presenting scores or information from regulations, format it in a readable way.
    If using search_kma_regulations, cite the sources in your answer when appropriate.
    """

    # Create model
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)

    # Define our message state
    class State(TypedDict):
        messages: Annotated[list, add_messages]
        student_code: Optional[str]
        student_name: Optional[str]
        student_class: Optional[str]
        scores: List[Dict[str, Any]]
        average_scores: Dict[str, Any]
        rag_results: List[Dict[str, Any]]
        current_task: Optional[str]
        current_tool: Optional[str]
        awaiting_human_input: bool
        human_input_prompt: Optional[str]

    # Define graph
    workflow = StateGraph(State)

    # Define nodes

    def chatbot(state: State):
        """Process messages and decide next action"""

        # Check if we're waiting for human input
        if state.get("awaiting_human_input", False):
            return {"awaiting_human_input": True, "human_input_prompt": state.get("human_input_prompt")}

        # Get messages for the LLM
        messages = state.get("messages", [])
        if not messages:
            return {"messages": []}

        # Add system message
        full_messages = [SystemMessage(content=system_prompt)] + messages

        # Call the LLM with tools
        response = llm_with_tools.invoke(full_messages)

        # Return the response with updated messages
        return {"messages": [response]}

    def handle_human_input(state: State):
        """Process human input when the agent is waiting for it"""

        # Get the latest human message
        messages = state.get("messages", [])
        if not messages:
            return state

        last_message = messages[-1]
        if not isinstance(last_message, HumanMessage):
            return state

        # Extract human input
        human_input = last_message.content

        # Check if we need to set the student code
        current_tool = state.get("current_tool")
        if current_tool in ["get_student_scores", "get_student_info"]:
            # Save student code
            updated_state = state.copy()
            updated_state["student_code"] = human_input.strip()
            updated_state["awaiting_human_input"] = False
            updated_state["human_input_prompt"] = None
            return updated_state

        # Default case - just clear awaiting flag
        updated_state = state.copy()
        updated_state["awaiting_human_input"] = False
        updated_state["human_input_prompt"] = None
        return updated_state

    # Create tool node for executing tools
    tool_node = ToolNode(tools)

    # Decision function for checking if we need to request human input
    def check_need_human_input(state: State):
        """Check if we need to request human input from the user"""

        # Check the last message for tool calls
        messages = state.get("messages", [])
        if not messages:
            return "no_input_needed"

        last_message = messages[-1]

        # If not an AI message with tool calls, no input needed
        if not (hasattr(last_message, "tool_calls") and last_message.tool_calls):
            return "no_input_needed"

        # Check if tool calls require student code
        tool_calls = last_message.tool_calls
        student_code = state.get("student_code")

        for tool_call in tool_calls:
            if tool_call["name"] in ["get_student_scores", "get_student_info"]:
                # Check if student code is in args and not provided
                if (("student_code" in tool_call["args"] and not tool_call["args"].get(
                        "student_code")) and not student_code):
                    # Need to request student code
                    return "request_student_code"

                # If we have student code but it's not in the args, add it
                if student_code and "student_code" in tool_call["args"] and not tool_call["args"].get("student_code"):
                    tool_call["args"]["student_code"] = student_code

        return "no_input_needed"

    def request_student_code(state: State):
        """Request student code from the user"""
        updated_state = state.copy()
        updated_state["awaiting_human_input"] = True
        updated_state["human_input_prompt"] = "Please provide your student code:"
        updated_state["current_tool"] = "get_student_info"  # Set current tool
        return updated_state

    # Process tool results to update state
    def process_tool_results(state: State):
        """Process tool results and update state data"""

        messages = state.get("messages", [])
        if not messages:
            return state

        # Find tool messages
        tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
        if not tool_messages:
            return state

        # Get the latest tool messages
        updated_state = state.copy()

        for tool_message in tool_messages:
            try:
                # Parse the tool result
                result_data = json.loads(tool_message.content)

                # Process based on tool type
                if tool_message.name == "get_student_scores":
                    if "scores" in result_data:
                        updated_state["scores"] = result_data["scores"]

                elif tool_message.name == "get_student_info":
                    if "student" in result_data and result_data["student"]:
                        student = result_data["student"]
                        updated_state["student_code"] = student.get("student_code", updated_state.get("student_code"))
                        updated_state["student_name"] = student.get("student_name", updated_state.get("student_name"))
                        updated_state["student_class"] = student.get("student_class",
                                                                     updated_state.get("student_class"))

                elif tool_message.name == "calculate_average_scores":
                    if "overall_average" in result_data:
                        updated_state["average_scores"] = result_data

                elif tool_message.name == "search_kma_regulations":
                    # Store the RAG results in a field we might want to track later
                    if "answer" in result_data:
                        if not "rag_results" in updated_state:
                            updated_state["rag_results"] = []
                        updated_state["rag_results"].append(
                            {"answer": result_data.get("answer", ""), "sources": result_data.get("sources", [])})

            except Exception as e:
                # If we can't parse the result, just continue
                pass

        return updated_state

    # Add nodes to graph
    workflow.add_node("chatbot", chatbot)
    workflow.add_node("tool_executor", tool_node)
    workflow.add_node("request_student_code", request_student_code)
    workflow.add_node("handle_human_input", handle_human_input)
    workflow.add_node("process_tool_results", process_tool_results)

    # Define conditional edges

    # From chatbot, check if tools are called
    def chatbot_condition(state: State):
        """Route based on tool calls in the last message"""
        messages = state.get("messages", [])
        if not messages:
            return "end"

        last_message = messages[-1]

        # Check for tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            # Check if we need to request human input
            need_input = check_need_human_input(state)
            if need_input == "request_student_code":
                return "request_student_code"
            else:
                return "tool_executor"

        # No tool calls, we're done
        return "end"

    # Add conditional edges
    workflow.add_conditional_edges("chatbot", chatbot_condition,
        {"tool_executor": "tool_executor", "request_student_code": "request_student_code", "end": END})

    # Add other edges
    workflow.add_edge("tool_executor", "process_tool_results")
    workflow.add_edge("process_tool_results", "chatbot")
    workflow.add_edge("request_student_code", END)  # End to wait for human input
    workflow.add_edge("handle_human_input", "chatbot")
    workflow.add_edge(START, "chatbot")

    # Compile graph
    app = workflow.compile()

    # Create a wrapper function to handle the human-in-the-loop behavior
    async def invoke_agent(state: MyAgentState):
        """Invoke the agent with proper handling of human-in-the-loop"""

        # Create initial state for the graph
        graph_state = {"messages": state.messages, "student_code": state.student_code,
            "student_name": state.student_name, "student_class": state.student_class, "scores": state.scores,
            "average_scores": state.average_scores, "rag_results": state.rag_results,  # Add RAG results
            "current_task": state.current_task, "current_tool": state.current_tool,
            "awaiting_human_input": state.awaiting_human_input, "human_input_prompt": state.human_input_prompt}

        # Invoke the graph
        result = app.invoke(graph_state)

        # Convert back to MyAgentState
        state.messages = result.get("messages", [])
        state.student_code = result.get("student_code", state.student_code)
        state.student_name = result.get("student_name", state.student_name)
        state.student_class = result.get("student_class", state.student_class)
        state.scores = result.get("scores", state.scores)
        state.average_scores = result.get("average_scores", state.average_scores)
        state.rag_results = result.get("rag_results", state.rag_results)  # Get RAG results
        state.current_task = result.get("current_task", state.current_task)
        state.current_tool = result.get("current_tool", state.current_tool)
        state.awaiting_human_input = result.get("awaiting_human_input", False)
        state.human_input_prompt = result.get("human_input_prompt", None)

        return state

    return invoke_agent


# Example usage
if __name__ == "__main__":
    # Create agent
    agent = create_supervisor_agent()

    # Set initial state
    state = MyAgentState()

    # Add initial message
    state.add_message(HumanMessage(content="What is my GPA for the last semester?"))

    # Run agent
    result = asyncio.run(agent(state))

    # Check if we need human input
    if result.awaiting_human_input:
        print(f"Agent is waiting for input: {result.human_input_prompt}")
        human_input = input("> ")

        # Process human input
        state.add_message(HumanMessage(content=human_input))
        state.set_human_input_received()

        # Continue execution
        result = asyncio.run(agent(result))

    # Print final messages
    for message in result.messages:
        if isinstance(message, AIMessage):
            print(f"AI: {message.content}")
        elif isinstance(message, HumanMessage):
            print(f"Human: {message.content}")
        elif isinstance(message, ToolMessage):
            print(f"Tool ({message.name}): {message.content[:100]}...")

    # Print final state
    print("\nFinal State:")
    print(f"Student Code: {result.student_code}")
    print(f"Student Name: {result.student_name}")
    print(f"Student Class: {result.student_class}")
    print(f"Number of Scores: {len(result.scores)}")
    if result.average_scores:
        print(f"Overall Average: {result.average_scores.get('overall_average', {})}")
