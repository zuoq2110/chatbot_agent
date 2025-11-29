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
with open(os.path.join(prompts_dir, "system_prompt.txt"), "r", encoding="utf-8") as f:
    react_prompt = f.read().strip()


def get_tool_descriptions(tools_list: list) -> str:
    descriptions = "\n".join([
        f"- {tool.name}: {tool.description} (args: {tool.args_schema.schema()['properties'].keys() if tool.args_schema else 'None'})"
        for tool in tools_list])
    logger.info(f"--- AGENT: Available tools: {[tool.name for tool in tools_list]} ---")
    return descriptions

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
    llm = get_llm()  # Use factory method to support runtime model switching
    
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
    tool_descriptions = get_tool_descriptions(tools)
    logger.info(f"Available tools: {[tool.name for tool in tools]}")
    logger.info(f"Tool descriptions length: {len(tool_descriptions)}")
    
    # FORCE tool call for regulation keywords
    last_message = state["messages"][-1] if state["messages"] else None
    force_tool_call = False
    
    if last_message and isinstance(last_message, HumanMessage):
        query_lower = last_message.content.lower()
        regulation_keywords = [
            'quy định', 'quy chế', 'chính sách', 'điều kiện', 'tiêu chuẩn',
            'hành vi', 'đình chỉ', 'kỷ luật', 'phúc khảo', 'thi', 'kiểm tra',
            'tốt nghiệp', 'rèn luyện', 'học tập', 'thủ tục', 'xét', 'công nhận',
            'quyết định', 'ban hành', 'điều', 'khoản', 'văn bản',
            # Academic keywords
            'chứng chỉ', 'bằng cấp', 'tiếng anh', 'toeic', 'ielts', 'vstep',
            'tín chỉ', 'điểm', 'học phần', 'môn học', 'khóa luận',
            # Process keywords  
            'đăng ký', 'nộp', 'hồ sơ', 'giấy tờ', 'mẫu đơn'
        ]
        
        if any(keyword in query_lower for keyword in regulation_keywords):
            force_tool_call = True
            logger.info(f"🔴 DETECTED REGULATION KEYWORDS - FORCING tool call for: {last_message.content[:100]}")
    
    # If forcing tool call, inject it directly
    if force_tool_call:
        from langchain_core.messages import ToolMessage
        
        # Extract query
        query = last_message.content
        
        # Determine department from keywords
        department = None
        if any(kw in query_lower for kw in ['thi', 'kiểm tra', 'đình chỉ', 'phúc khảo', 'khảo thí']):
            department = 'phongkhaothi'
        elif any(kw in query_lower for kw in ['đào tạo', 'tốt nghiệp', 'học tập', 'tín chỉ']):
            department = 'phongdaotao'
        
        # Call RAG tool directly
        logger.info(f"⚡ FORCING search_kma_regulations: query='{query}', department='{department}'")
        
        try:
            # Import and call tool directly
            from rag import search_kma_regulations
            result = search_kma_regulations.invoke({
                "query": query, 
                "department": department  # None is now valid
            })
            
            # Create response message with result
            response_message = AIMessage(content=result)
            logger.info(f"✅ Forced tool call successful, result length: {len(result)}")
            
            return {"messages": state['messages'] + [response_message]}
            
        except Exception as e:
            logger.error(f"❌ Forced tool call failed: {e}")
            # Fall through to normal LLM call
    
    # Normal LLM call with few-shot examples
    few_shot_examples = """

### VÍ DỤ MINH HỌA (BẮT BUỘC HỌC THEO)

**Ví dụ 1: Câu hỏi về quy định**
User: "Những hành vi nào bị đình chỉ thi?"
Assistant: [Phải gọi search_kma_regulations]
Action: search_kma_regulations
Action Input: query="hành vi bị đình chỉ thi", department="phongkhaothi"

**Ví dụ 2: Câu hỏi về điều kiện**
User: "Điều kiện tốt nghiệp là gì?"
Assistant: [Phải gọi search_kma_regulations]
Action: search_kma_regulations
Action Input: query="điều kiện tốt nghiệp", department="phongdaotao"

**Ví dụ 3: Câu hỏi về thủ tục**
User: "Thủ tục phúc khảo như thế nào?"
Assistant: [Phải gọi search_kma_regulations]
Action: search_kma_regulations
Action Input: query="thủ tục phúc khảo", department="phongkhaothi"
"""
    
    enhanced_prompt = react_prompt.format(tool_descriptions=tool_descriptions) + few_shot_examples
    
    prompt = ChatPromptTemplate.from_messages(
        [("system", enhanced_prompt),
         MessagesPlaceholder(variable_name="messages"), ])

    # Bind tools and structured output - use factory method for runtime model switching
    model_with_tools = get_llm().bind_tools(tools)
    chains = prompt | model_with_tools

    try:
        response = chains.invoke({"messages": state["messages"]})
        
        # Log tool calls for debugging
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"--- AGENT: Tool calls detected: {[tool_call.get('name', 'unknown') for tool_call in response.tool_calls]} ---")
        else:
            logger.info("--- AGENT: No tool calls detected ---")
            logger.info(f"Response content preview: {response.content[:200]}...")
            
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
