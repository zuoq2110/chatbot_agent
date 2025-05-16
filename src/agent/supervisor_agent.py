import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import MyAgentState
from rag import create_rag_tool
from llm.config import get_gemini_llm
from score import get_student_scores, get_student_info, calculate_average_scores

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define tools
score_tool = get_student_scores
student_info_tool = get_student_info
rag_tool = create_rag_tool()
calculator_tool = calculate_average_scores

# Get all tools
tools = [score_tool, student_info_tool, calculator_tool, rag_tool]

# Load prompts
prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
with open(os.path.join(prompts_dir, "react_prompt.txt"), "r") as f:
    react_prompt = f.read().strip()


def get_tool_descriptions(tools_list: list) -> str:
    return "\n".join([
        f"- {tool.name}: {tool.description} (args: {tool.args_schema.schema()['properties'].keys() if tool.args_schema else 'None'})"
        for tool in tools_list])


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

    def create_graph(self):
        # Create the state graph
        logger.info("___Creating workflow graph___")

        workflow = StateGraph(self.state)
        workflow.add_node("agent", self.call_model_no_human_loop)
        workflow.add_node("action", self.tool_node)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", self.should_continue_no_human_loop, {"action": "action", END: END})
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
        initial_state = {"messages": [HumanMessage(content=init)]}

        if self.workflow is None:
            self.create_graph()
            self.print_mermaid()

        result = await self.workflow.ainvoke(initial_state)
        current_messages = result['messages']

        return current_messages
