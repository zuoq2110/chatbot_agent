import logging
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import MyAgentState
from llm.config import get_gemini_llm, get_llm
from rag import create_rag_tool
from score import get_student_scores, get_student_info, calculate_average_scores, calculate_gpa_from_db

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define tools
score_tool = get_student_scores
student_info_tool = get_student_info
rag_tool = create_rag_tool()
calculator_tool = calculate_gpa_from_db

# Get all tools
tools = [score_tool, student_info_tool, calculator_tool, rag_tool]

# Load prompts
prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
with open(os.path.join(prompts_dir, "system_prompt.txt"), "r", encoding="utf-8") as f:
    react_prompt = f.read().strip()


def get_tool_descriptions(tools_list: list) -> str:
    return "\n".join([
        f"- {tool.name}: {tool.description} (args: {tool.args_schema.schema()['properties'].keys() if tool.args_schema else 'None'})"
        for tool in tools_list])

# Query reformulation prompt
conversational_prompt = """
    Given a chat history between an AI chatbot and user
    that chatbot's message marked with [bot] prefix and user's message marked with [user] prefix,
    and given the latest user question which might reference context in the chat history,
    formulate a standalone question which can be understood without the chat history.
    Do NOT answer the question, just reformulate it if needed and otherwise return it as is.
    Keep the original language of the user's input (do NOT translate).
    
    ** History **
    This is chat history:
    {chat_history}
    
    ** Lateset user question **
    This is latest user question:
    {question}
    """


async def summarize_conversation(state: MyAgentState) -> MyAgentState:
    """
    Summarize conversation history to provide context for the next query.
    This helps the model understand the conversation flow.
    """
    logger.info("--- AGENT: Summarizing conversation history ---")
    
    messages = state["messages"]
    
    # If there are fewer than 3 messages, no need to summarize
    if len(messages) < 1:
        return state
    
    # The conversational context prompt helps rewrite the latest query with context
    llm = get_gemini_llm()
    
    # Format the chat history for the summarization prompt
    chat_history = []
    for i, msg in enumerate(messages[:-1]):  # Exclude the most recent message
        prefix = "[bot]" if isinstance(msg, AIMessage) else "[user]"
        chat_history.append(f"{prefix} {msg.content}")
    
    # Get the latest user query
    latest_query = messages[-1].content

    logger.info("--- AGENT: Summarizing conversation history ---")
    logger.info(f"Latest query: {latest_query}")
    logger.info(f"Chat history: {chat_history}")

    chat_history_str = "" + "\n".join(chat_history)

    if len(chat_history_str) == 0:
        return state

    logger.info(f"Chat history str: {chat_history_str}")
    
    # Invoke the rewriting prompt with the formatted chat history
    try:
        standalone_query = llm.invoke(
            conversational_prompt.format(
                chat_history=chat_history_str,
                question=latest_query
            )
        )
        
        # Replace the latest message with the reformulated query
        contextual_message = HumanMessage(content=standalone_query.content)

        logger.info("--- AGENT: Contextual message ---")
        logger.info(f"Contextual message: {contextual_message}")
        
        # Return new state with all previous messages and the reformulated query
        return {"messages": messages[:-1] + [contextual_message]}
    except Exception as e:
        logger.error(f"Error summarizing conversation: {e}")
        # If summarization fails, continue with original messages
        return state


async def call_model_no_human_loop(state: MyAgentState) -> MyAgentState:
    logger.info("--- AGENT (No Human Loop): Calling LLM ---")

    # Prepare the prompts
    prompt = ChatPromptTemplate.from_messages(
        [("system", react_prompt.format(tool_descriptions=get_tool_descriptions(tools))),
         MessagesPlaceholder(variable_name="messages"), ])

    # Bind tools and structured output
    model_with_tools = get_gemini_llm().bind_tools(tools)
    chains = prompt | model_with_tools

    try:
        response = chains.invoke({"messages": state["messages"]})
        return {"messages": state['messages'] + [response]}

    except Exception as e:
        logger.error(f"Error invoking LLM: {e}")
        error_message = AIMessage(content=f"An error occurred with the LLM: {e}")
        return {"messages": state['messages'] + [error_message]}


def should_continue_no_human_loop(state: MyAgentState):
    print("--- AGENT (No Human Loop): Deciding next step ---")
    last_message = state['messages'][-1] if state['messages'] else None
    if not last_message:  # Trường hợp state messages rỗng
        return END

    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "action"
    print("--- AGENT (No Human Loop): No tool call, ending. ---")
    return END


tool_node = ToolNode(tools)


class ReActGraph:
    def __init__(self):
        self.workflow = None
        self.state = MyAgentState
        self.tools = tools
        self.call_model_no_human_loop = call_model_no_human_loop
        self.tool_node = tool_node
        self.should_continue_no_human_loop = should_continue_no_human_loop
        self.conversation_memory = []

    def create_graph(self):
        # Create the state graph
        logger.info("___Creating workflow graph___")

        workflow = StateGraph(self.state)
        workflow.add_node("summarize", summarize_conversation)
        workflow.add_node("agent", self.call_model_no_human_loop)
        workflow.add_node("action", self.tool_node)
        
        # Set entry point to the summarization node
        workflow.set_entry_point("summarize")
        
        # After summarization, always go to agent
        workflow.add_edge("summarize", "agent")
        
        # From agent, conditionally go to action or end
        workflow.add_conditional_edges("agent", self.should_continue_no_human_loop, {"action": "action", END: END})
        
        # From action, always go back to agent
        workflow.add_edge("action", "agent")
        
        self.workflow = workflow.compile()

        logger.info("___Finished creating workflow graph___")
        return self.workflow

    def print_mermaid(self):
        # Generate and log the Mermaid diagram
        try:
            logger.info("___Printing mermaid graph___")
            mermaid_diagram = self.workflow.get_graph().draw_mermaid()
            logger.info("Mermaid diagram:")
            logger.info(mermaid_diagram)


            logger.info("___Saving mermaid graph to file___")
            current_dir = Path(__file__).parent.absolute()
            project_root = current_dir.parent.parent
            mermaid_dir_path = os.path.join(project_root, "mermaid")
            mermaid_path = os.path.join(mermaid_dir_path, "react_mermaid.mmd")

            ## Save the diagram to a file
            with open(mermaid_path, "w") as f:
                f.write(mermaid_diagram)
                f.close()

            logger.info("___Finished printing mermaid graph___")

        except Exception as e:
            print(f"Error generating Mermaid diagram: {str(e)}")

    async def chat(self, init: str):
        """Legacy method for single message processing, maintained for backward compatibility"""
        initial_state = {"messages": [HumanMessage(content=init)]}

        if self.workflow is None:
            self.create_graph()
            self.print_mermaid()

        result = await self.workflow.ainvoke(initial_state)
        current_messages = result['messages']

        return current_messages
        
    async def chat_with_memory(self, conversation_history: List[BaseMessage], query: str) -> List[BaseMessage]:
        """
        Process a query while maintaining conversation history.
        
        Args:
            conversation_history: Previous messages in the conversation
            query: The new user query to process
            
        Returns:
            Updated conversation history with the agent's response
        """
        # Add the new query to the conversation history
        updated_history = conversation_history.copy() + [HumanMessage(content=query)]
        
        # Prepare the initial state with the full conversation history
        initial_state = {"messages": updated_history}
        
        # Create the workflow if it doesn't exist
        if self.workflow is None:
            self.create_graph()
            self.print_mermaid()
            
        # Execute the workflow
        result = await self.workflow.ainvoke(initial_state)
        
        # Return the updated conversation history
        return result['messages']
