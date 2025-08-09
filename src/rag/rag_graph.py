# import logging
# import os
# import unicodedata
# from pathlib import Path
# from typing import Literal, Dict, Any

# from langchain_core.messages import HumanMessage, AIMessage
# from langgraph.graph import MessagesState
# from langgraph.graph import StateGraph, START, END
# from langsmith import Client
# from pydantic import Field, BaseModel

# from llm import LLMConfig, get_llm
# from rag.retriever import create_hybrid_retriever

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


# class GradeDocuments(BaseModel):
#     """Grade documents using a binary score for relevance check."""
#     binary_score: str = Field(description="Relevance score: 'yes' if relevant, or 'no' if not relevant")


# # Helper function for score_tool.py to use
# async def process_kma_query(query: str, retriever=None, llm=None) -> Dict[str, Any]:
#     """Process a KMA regulation query and return the answer with sources.
    
#     Args:
#         query: The question to answer
#         retriever: Optional retriever to use (will create one if not provided)
#         llm: Optional LLM to use (will create one if not provided)
        
#     Returns:
#         Dictionary with answer and sources
#     """
#     # Create components if not provided
#     if retriever is None:
#         retriever = get_retriever()

#     if llm is None:
#         llm = LLMConfig.create_rag_llm()

#     # Load prompts
#     prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
#     with open(os.path.join(prompts_dir, "generate.txt"), "r") as f:
#         generate_prompt = f.read().strip()

#     # Retrieve documents
#     docs = retriever.get_relevant_documents(query)

#     # Combine document content
#     context = "\n\n".join([doc.page_content for doc in docs])

#     # Generate answer
#     prompt = generate_prompt.format(question=query, context=context)
#     response = llm.invoke([{"role": "user", "content": prompt}])

#     # Return the answer and sources
#     return {"answer": response.content, "sources": [doc.page_content for doc in docs[:3]]  # Return top 3 sources
#     }


# def get_retriever():
#     """Get the hybrid retriever for KMA regulations"""
#     # Define paths
#     current_dir = Path(__file__).parent.absolute()
#     project_root = current_dir.parent.parent
#     vector_db_path = os.path.join(project_root, "vector_db")
#     data_path = os.path.join(project_root, "data", "regulation.txt")

#     hybrid_retriever, _ = create_hybrid_retriever(vector_db_path=vector_db_path, data_path=data_path)

#     return hybrid_retriever


# class KMAChatAgent:
#     def __init__(self, model_name="qwen3:8b", project_name="KMARegulation"):
#         """Initialize the KMA Chat Agent with a hybrid retriever and model"""
#         # Initialize LangSmith client
#         self.langsmith_client = Client()

#         # Initialize callback manager with LangSmith tracer
#         self.callback_manager = LLMConfig.create_callback_manager(project_name)

#         # Create models using the LLMConfig
#         self.llm = LLMConfig.create_rag_llm(model_name, self.callback_manager)
#         self.grader_model = LLMConfig.create_rag_llm(model_name, self.callback_manager)

#         # Store the retriever directly
#         self.retriever = self.get_retriever()

#         # Load prompts from files
#         self.prompts = self._load_prompts()

#         # Build the workflow
#         self.workflow = StateGraph(MessagesState)
#         self.graph = self._build_workflow()

#     def _load_prompts(self):
#         """Load all prompts from text files"""
#         prompts = {}
#         prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")

#         # Load grade prompts
#         with open(os.path.join(prompts_dir, "grade.txt"), "r") as f:
#             prompts["grade"] = f.read().strip()

#         # Load rewrite prompts
#         with open(os.path.join(prompts_dir, "rewrite.txt"), "r") as f:
#             prompts["rewrite"] = f.read().strip()

#         # Load generate prompts
#         with open(os.path.join(prompts_dir, "generate.txt"), "r") as f:
#             prompts["generate"] = f.read().strip()

#         return prompts

#     def get_retriever(self):
#         """Get the hybrid retriever"""
#         return get_retriever()

#     def _build_workflow(self):
#         """Build the LangGraph workflow"""
#         workflow = self.workflow

#         # Define the nodes
#         workflow.add_node(self.process_user_query)
#         workflow.add_node(self.retrieve_documents)
#         workflow.add_node(self.rewrite_question)
#         workflow.add_node(self.generate_answer)

#         # Set up edges
#         workflow.add_edge(START, "process_user_query")
#         workflow.add_edge("process_user_query", "retrieve_documents")

#         # Conditional edges after retrieval
#         workflow.add_conditional_edges("retrieve_documents", self.grade_documents,
#             {"generate_answer": "generate_answer", "rewrite_question": "rewrite_question"})

#         workflow.add_edge("generate_answer", END)
#         workflow.add_edge("rewrite_question", "process_user_query")

#         # Log the workflow structure
#         logger.info("Workflow structure created with nodes and edges")

#         # Compile the graph
#         try:
#             graph = workflow.compile()
#             logger.info("Workflow graph compiled successfully")
#         except Exception as e:
#             logger.error(f"Error compiling workflow graph: {str(e)}")
#             raise

#         # Generate and log the Mermaid diagram
#         try:
#             mermaid_diagram = graph.get_graph().draw_mermaid()
#             logger.info("Mermaid diagram:")
#             logger.info(mermaid_diagram)

#             logger.info("Saving Mermaid diagram to file")
#             current_dir = Path(__file__).parent.absolute()
#             project_root = current_dir.parent.parent
#             mermaid_dir_path = os.path.join(project_root, "mermaid")
#             mermaid_path = os.path.join(mermaid_dir_path, "rag_mermaid.mmd")

#             # Save the diagram to a file
#             with open(mermaid_path, "w") as f:
#                 f.write(mermaid_diagram)
#                 f.close()

#             logger.info("Mermaid diagram saved successfully")

#         except Exception as e:
#             logger.error(f"Error generating Mermaid diagram: {str(e)}")

#         return graph

#     def process_user_query(self, state: MessagesState):
#         """Process the user query for retrieval"""
#         # Normalize the query for better processing
#         if state["messages"] and len(state["messages"]) > 0:
#             query = state["messages"][0].content
#             normalized_query = unicodedata.normalize('NFC', query)
#             state["messages"][0].content = normalized_query
#         return {"messages": state["messages"]}

#     def retrieve_documents(self, state: MessagesState):
#         """Directly retrieve documents using the retriever"""
#         query = state["messages"][0].content
#         # Get documents from the retriever
#         docs = self.retriever.get_relevant_documents(query)
#         # Combine document content
#         combined_content = "\n\n".join([doc.page_content for doc in docs])
#         # Add the retrieved content as a system message
#         retrieval_message = AIMessage(content=combined_content)
#         # Update the state with the retrieved documents
#         return {"messages": state["messages"] + [retrieval_message]}

#     def grade_documents(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
#         """Determine whether the retrieved documents are relevant to the question"""
#         question = state["messages"][0].content
#         context = state["messages"][-1].content

#         prompt = self.prompts["grade"].format(question=question, context=context)

#         response = self.grader_model.with_structured_output(GradeDocuments).invoke(
#             [{"role": "user", "content": prompt}])
#         score = response.binary_score

#         if score == "yes":
#             return "generate_answer"
#         else:
#             return "rewrite_question"

#     def rewrite_question(self, state: MessagesState):
#         """Rewrite the original user question"""
#         messages = state["messages"]
#         question = messages[0].content
#         prompt = self.prompts["rewrite"].format(question=question)
#         response = self.llm.invoke([{"role": "user", "content": prompt}])
#         return {"messages": [HumanMessage(content=response.content)]}

#     def generate_answer(self, state: MessagesState):
#         """Generate an answer"""
#         question = state["messages"][0].content
#         context = state["messages"][-1].content
#         prompt = self.prompts["generate"].format(question=question, context=context)
#         response = self.llm.invoke([{"role": "user", "content": prompt}])
#         return {"messages": state["messages"][:-1] + [response]}

#     def chat(self, message):
#         """Process a single chat message and return the response"""
#         query = {"messages": [HumanMessage(content=message)]}
#         response = self.graph.invoke(query)
#         return response["messages"][-1].content

# Toggle comment for deploy to Streamlit or LangGraph UI
# graph = KMAChatAgent()

import logging
import os
import unicodedata
from pathlib import Path
from typing import Literal, Dict, Any

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langsmith import Client
from pydantic import Field, BaseModel

# Đảm bảo bạn đã import get_gemini_llm từ llm.py
from llm import LLMConfig, get_gemini_llm 
from rag.retriever import create_hybrid_retriever

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(description="Relevance score: 'yes' if relevant, or 'no' if not relevant")


# Helper function for score_tool.py to use
async def process_kma_query(query: str, retriever=None, llm=None) -> Dict[str, Any]:
    """Process a KMA regulation query and return the answer with sources.
    
    Args:
        query: The question to answer
        retriever: Optional retriever to use (will create one if not provided)
        llm: Optional LLM to use (will create one if not provided)
        
    Returns:
        Dictionary with answer and sources
    """
    # Create components if not provided
    if retriever is None:
        retriever = get_retriever()

    if llm is None:
        # Trong hàm trợ giúp này, nếu LLM không được cung cấp,
        # chúng ta sẽ sử dụng Gemini làm mặc định thay vì ChatOllama
        llm = get_gemini_llm(model_name=LLMConfig.DEFAULT_GEMINI_MODEL) 

    # Load prompts
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
    with open(os.path.join(prompts_dir, "generate.txt"), "r") as f:
        generate_prompt = f.read().strip()

    # Retrieve documents
    docs = retriever.get_relevant_documents(query)

    # Combine document content
    context = "\n\n".join([doc.page_content for doc in docs])

    # Generate answer
    prompt = generate_prompt.format(question=query, context=context)
    response = llm.invoke([{"role": "user", "content": prompt}])

    # Return the answer and sources
    return {"answer": response.content, "sources": [doc.page_content for doc in docs[:3]]  # Return top 3 sources
    }


def get_retriever():
    """Get the hybrid retriever for KMA regulations"""
    # Define paths
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    vector_db_path = os.path.join(project_root, "vector_db")
    data_dir = os.path.join(project_root, "data")

    hybrid_retriever, _ = create_hybrid_retriever(vector_db_path=vector_db_path, data_dir=data_dir)
    return hybrid_retriever


class KMAChatAgent:
    def __init__(self, model_name: str = None, project_name="KMARegulation"):
        """Initialize the KMA Chat Agent with a hybrid retriever and model"""
        # Initialize LangSmith client
        self.langsmith_client = Client()

        # Initialize callback manager with LangSmith tracer
        self.callback_manager = LLMConfig.create_callback_manager(project_name)

        # Create models using get_gemini_llm
        # Nếu model_name không được cung cấp, get_gemini_llm sẽ dùng DEFAULT_GEMINI_MODEL
        # Hãy đảm bảo hàm get_gemini_llm trong llm.py đã được cập nhật để chấp nhận các tham số
        # model_name và callback_manager như đã sửa đổi trước đó.
        if model_name is None:
            model_name = LLMConfig.DEFAULT_GEMINI_MODEL # Sử dụng mặc định của Gemini nếu không có tên model cụ thể được truyền vào

        try:
            self.llm = get_gemini_llm(model_name=model_name, callback_manager=self.callback_manager)
            # Sử dụng cùng mô hình cho grader, Gemini thường tốt với structured_output
            self.grader_model = get_gemini_llm(model_name=model_name, callback_manager=self.callback_manager)
            logger.info(f"Initialized LLMs with Gemini model: {model_name}")
        except ValueError as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}. Please ensure GOOGLE_API_KEY is set and valid.")
            raise # Re-raise error to stop initialization if LLM fails


        # Store the retriever directly
        self.retriever = self.get_retriever()

        # Load prompts from files
        self.prompts = self._load_prompts()

        # Build the workflow
        self.workflow = StateGraph(MessagesState)
        self.graph = self._build_workflow()

    def _load_prompts(self):
        """Load all prompts from text files"""
        prompts = {}
        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")

        # Load grade prompts
        with open(os.path.join(prompts_dir, "grade.txt"), "r") as f:
            prompts["grade"] = f.read().strip()

        # Load rewrite prompts
        with open(os.path.join(prompts_dir, "rewrite.txt"), "r") as f:
            prompts["rewrite"] = f.read().strip()

        # Load generate prompts
        with open(os.path.join(prompts_dir, "generate.txt"), "r") as f:
            prompts["generate"] = f.read().strip()

        return prompts

    def get_retriever(self):
        """Get the hybrid retriever"""
        return get_retriever()

    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = self.workflow

        # Define the nodes
        workflow.add_node("process_user_query", self.process_user_query) # Thêm tên node rõ ràng
        workflow.add_node("retrieve_documents", self.retrieve_documents)
        workflow.add_node("rewrite_question", self.rewrite_question)
        workflow.add_node("generate_answer", self.generate_answer)

        # Set up edges
        workflow.add_edge(START, "process_user_query")
        workflow.add_edge("process_user_query", "retrieve_documents")

        # Conditional edges after retrieval
        workflow.add_conditional_edges("retrieve_documents", self.grade_documents,
            {"generate_answer": "generate_answer", "rewrite_question": "rewrite_question"})

        workflow.add_edge("generate_answer", END)
        workflow.add_edge("rewrite_question", "process_user_query")

        # Log the workflow structure
        logger.info("Workflow structure created with nodes and edges")

        # Compile the graph
        try:
            graph = workflow.compile()
            logger.info("Workflow graph compiled successfully")
        except Exception as e:
            logger.error(f"Error compiling workflow graph: {str(e)}")
            raise

        # Generate and log the Mermaid diagram
        try:
            mermaid_diagram = graph.get_graph().draw_mermaid()
            logger.info("Mermaid diagram:")
            logger.info(mermaid_diagram)

            logger.info("Saving Mermaid diagram to file")
            current_dir = Path(__file__).parent.absolute()
            project_root = current_dir.parent.parent
            mermaid_dir_path = os.path.join(project_root, "mermaid")
            os.makedirs(mermaid_dir_path, exist_ok=True) # Đảm bảo thư mục tồn tại
            mermaid_path = os.path.join(mermaid_dir_path, "rag_mermaid.mmd")

            # Save the diagram to a file
            with open(mermaid_path, "w") as f:
                f.write(mermaid_diagram)
                f.close()

            logger.info("Mermaid diagram saved successfully")

        except Exception as e:
            logger.error(f"Error generating Mermaid diagram: {str(e)}")

        return graph

    def process_user_query(self, state: MessagesState):
        """Process the user query for retrieval"""
        # Normalize the query for better processing
        if state["messages"] and len(state["messages"]) > 0:
            query = state["messages"][0].content
            # Loại bỏ các ký tự dấu và chuẩn hóa Unicode để truy vấn hiệu quả hơn
            normalized_query = unicodedata.normalize('NFD', query).encode('ascii', 'ignore').decode('utf-8')
            state["messages"][0] = HumanMessage(content=normalized_query) # Tạo lại HumanMessage để đảm bảo tính nhất quán
        return state # Trả về toàn bộ state đã cập nhật

    def retrieve_documents(self, state: MessagesState):
        """Directly retrieve documents using the retriever"""
        query = state["messages"][0].content
        logger.info(f"Retrieving documents for query: {query}")
        # Get documents from the retriever
        docs = self.retriever.get_relevant_documents(query)
        # Combine document content
        combined_content = "\n\n".join([doc.page_content for doc in docs])
        # Add the retrieved content as a system message
        retrieval_message = AIMessage(content=combined_content, name="retrieved_context") # Đặt tên để dễ debug
        # Update the state with the retrieved documents
        logger.info(f"Retrieved {len(docs)} documents.")
        return {"messages": state["messages"] + [retrieval_message]}

    def grade_documents(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        """Determine whether the retrieved documents are relevant to the question"""
        question = state["messages"][0].content
        # Lấy ngữ cảnh từ tin nhắn AIMessage cuối cùng (có thể đặt tên cho nó)
        context_message = next((msg.content for msg in reversed(state["messages"]) if isinstance(msg, AIMessage) and msg.name == "retrieved_context"), "")
        
        if not context_message:
            logger.warning("No retrieved context found for grading. Assuming irrelevant.")
            return "rewrite_question"

        prompt = self.prompts["grade"].format(question=question, context=context_message)
        logger.info(f"Grading documents with prompt: {prompt[:100]}...") # Log một phần prompt

        try:
            # Gemini thường hỗ trợ structured_output tốt hơn TinyLlama
            response = self.grader_model.with_structured_output(GradeDocuments).invoke(
                [{"role": "user", "content": prompt}])
            score = response.binary_score
        except Exception as e:
            logger.error(f"Error grading documents with structured output: {e}. Defaulting to 'no'.")
            score = "no" # Fallback nếu structured output thất bại

        logger.info(f"Document grading score: {score}")
        if score == "yes":
            return "generate_answer"
        else:
            return "rewrite_question"

    def rewrite_question(self, state: MessagesState):
        """Rewrite the original user question"""
        messages = state["messages"]
        question = messages[0].content
        logger.info(f"Rewriting question: {question}")
        prompt = self.prompts["rewrite"].format(question=question)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        rewritten_question = response.content
        logger.info(f"Rewritten question: {rewritten_question}")
        # Cập nhật tin nhắn người dùng đầu tiên với câu hỏi đã viết lại
        return {"messages": [HumanMessage(content=rewritten_question)]}

    def generate_answer(self, state: MessagesState):
        """Generate an answer"""
        question = state["messages"][0].content
        # Tìm ngữ cảnh đã lấy được
        context_message = next((msg.content for msg in reversed(state["messages"]) if isinstance(msg, AIMessage) and msg.name == "retrieved_context"), "")

        if not context_message:
            logger.warning("No context found for answer generation. Generating with only question.")
            context_message = "Không có thông tin liên quan được tìm thấy trong cơ sở dữ liệu." # Fallback context

        prompt = self.prompts["generate"].format(question=question, context=context_message)
        logger.info(f"Generating answer with prompt: {prompt[:100]}...") # Log một phần prompt
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        logger.info(f"Generated answer.")
        return {"messages": state["messages"][:-1] + [response]} # Xóa context message trước khi thêm câu trả lời cuối cùng

    def chat(self, message):
        """Process a single chat message and return the response"""
        query = {"messages": [HumanMessage(content=message)]}
        logger.info(f"Starting chat for query: {message}")
        try:
            # `invoke` sẽ chạy qua toàn bộ đồ thị
            response = self.graph.invoke(query)
            final_answer = response["messages"][-1].content
            logger.info(f" {final_answer[:100]}...")
            return final_answer
        except Exception as e:
            logger.error(f"Error during chat processing: {str(e)}")
            return f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"

# Toggle comment for deploy to Streamlit or LangGraph UI
# graph = KMAChatAgent()