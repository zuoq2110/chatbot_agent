import unicodedata
from typing import Literal

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain_core.tools import create_retriever_tool
from langchain_ollama import ChatOllama
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langsmith import Client
from pydantic import Field, BaseModel

# Constants for prompts
GRADE_PROMPT = (
    """
    ** Context **
    You are a grader assessing relevance of a retrieved document to a user question that all in vietnamese or another language.
    user's question is about regulations and policies of the Academy of Cryptographic Techniques (KMA).
    Your user is a student or lecturer of KMA.
    You will be given a document and a question.
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant.
    
    ** Objective **
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
    
    ** Document **
    {context}
    
    ** Question **
    {question}
    """
)

REWRITE_PROMPT = (
    """
    ** Context **
    You are an AI assistant that rewrites user questions to improve clarity and relevance.
    The questions are about regulations and policies of the Academy of Cryptographic Techniques (KMA).
    You are given a question that may be unclear or not directly related to the regulations.
    Look at the input and try to reason about the underlying semantic intent / meaning.
    Please rewrite the question to make it clearer and more relevant.
    
    ** Objective **
    Please rewrite the question to make it clearer and more relevant. Formulate an improved question.
    
    ** Constraints **
    - Make sure to keep the context of the question intact.
    - And make sure re-write question is same language with original question.
    - Please write only improved question without another words or informations.
    
    ** Question **
    Here is the initial question:
    {question}
    """
)

GENERATE_PROMPT = (
    """** Context **
    Bạn là một trợ lý ảo dành cho sinh viên và giảng viên của Học viện Kỹ thuật mật mã (viết tắt là KMA).
    Bạn có hiểu biết về tất cả các quy định và chính sách của trường và có thể trả lời với bất kỳ câu hỏi nào về chúng.
    Bạn sẽ dựa trên thông tin từ tài liệu được cung cấp bên dưới để trả lời câu hỏi của người dùng về những quy định và chính sách của KMA.
    
    ** Objective **
    - Hãy trả lời các câu hỏi về quy định và chính sách của KMA.
    - Nếu không thể trả lời, hãy nói rằng bạn không thể trả lời câu hỏi đó.
    
    ** Tone **
    - Hãy trả lời các câu hỏi dưới vai trò một trợ lý ảo thông minh và chuyên nghiệp. Trả lời chính xác, ngắn gọn và đầy đủ thông tin.
    - Chỉ trả lời về các thông tin được hỏi mà không đưa ra bất kỳ lời chào, lời khuyên hay lời cảm ơn nào.
    - Hãy trả lời các câu hỏi bằng tiếng Việt.
    - Hãy trình bày câu trả lời dưới dạng có format, có cấu trúc (sử dụng markdown nếu cần), dễ nhìn và dễ hiểu.
    
    ** Question **
    - Câu hỏi của người dùng là:
    {question}
    
    ** Document **
    - Dưới đây là thông tin về quy định và chính sách của KMA liên quan đến câu hỏi:
    {context}
    """
)

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(description="Relevance score: 'yes' if relevant, or 'no' if not relevant")


class KMAChatAgent:
    def __init__(self, hybrid_retriever, model_name="llama3.2", project_name="KMARegulation"):
        """Initialize the KMA Chat Agent with a hybrid retriever and model"""
        # Initialize LangSmith client
        self.langsmith_client = Client()
        
        # Initialize callback manager with LangSmith tracer
        self.callback_manager = CallbackManager([LangChainTracer(project_name=project_name)])
        
        # Create models
        self.llm = ChatOllama(model=model_name)
        self.grader_model = ChatOllama(model=model_name)
        
        # Create retriever tool
        self.retriever_tool = create_retriever_tool(
            hybrid_retriever, 
            name="KMARegulationRetriever",
            description="A tool to retrieve information from KMA regulations and rules."
        )
        
        # Build the workflow
        self.graph = self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(MessagesState)
        
        # Define the nodes
        workflow.add_node(self.generate_query_or_respond)
        workflow.add_node("retrieve", ToolNode([self.retriever_tool]))
        workflow.add_node(self.rewrite_question)
        workflow.add_node(self.generate_answer)
        
        # Set up edges
        workflow.add_edge(START, "generate_query_or_respond")
        
        # Decide whether to retrieve
        workflow.add_conditional_edges(
            "generate_query_or_respond",
            tools_condition,
            {
                "tools": "retrieve", 
                END: END,
            },
        )
        
        # Edges taken after the `action` node is called
        workflow.add_conditional_edges(
            "retrieve",
            self.grade_documents,
        )
        
        workflow.add_edge("generate_answer", END)
        workflow.add_edge("rewrite_question", "generate_query_or_respond")
        
        # Compile the graph
        return workflow.compile()
    
    def generate_query_or_respond(self, state: MessagesState):
        """Generate a query or respond to the user"""
        ai = self.llm.bind_tools([self.retriever_tool])

        normalized_query = unicodedata.normalize('NFC', state["messages"][0].content)
        state["messages"][0].content = normalized_query

        response = ai.invoke(state["messages"])

        print("--"*50)
        print("original messages")
        print(state["messages"])

        # Check if the response is a tool call
        print("--"*50)
        print(response)
        print("--"*50)

        return {"messages": [response]}
    
    def grade_documents(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        """Determine whether the retrieved documents are relevant to the question"""
        question = state["messages"][0].content
        context = state["messages"][-1].content
        
        prompt = GRADE_PROMPT.format(question=question, context=context)
        
        response = self.grader_model.with_structured_output(GradeDocuments).invoke(
            [{"role": "user", "content": prompt}]
        )
        score = response.binary_score
        
        if score == "yes":
            return "generate_answer"
        else:
            return "rewrite_question"
    
    def rewrite_question(self, state: MessagesState):
        """Rewrite the original user question"""
        messages = state["messages"]
        question = messages[0].content
        prompt = REWRITE_PROMPT.format(question=question)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": [{"role": "user", "content": response.content}]}
    
    def generate_answer(self, state: MessagesState):
        """Generate an answer"""
        question = state["messages"][0].content
        context = state["messages"][-1].content
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}
    
    def chat(self, message):
        """Process a single chat message and return the response"""
        query = {"messages": [{"role": "user", "content": message}]}
        response = self.graph.invoke(query)
        return response["messages"][-1].content 