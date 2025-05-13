import os
import unicodedata
import logging
from typing import Literal

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langsmith import Client
from pydantic import Field, BaseModel

from llm_config import LLMConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(description="Relevance score: 'yes' if relevant, or 'no' if not relevant")


class KMAChatAgent:
    def __init__(self, hybrid_retriever, model_name="llama3.2", project_name="KMARegulation"):
        """Initialize the KMA Chat Agent with a hybrid retriever and model"""
        # Initialize LangSmith client
        self.langsmith_client = Client()
        
        # Initialize callback manager with LangSmith tracer
        self.callback_manager = LLMConfig.create_callback_manager(project_name)
        
        # Create models using the LLMConfig
        self.llm = LLMConfig.create_llm(model_name, self.callback_manager)
        self.grader_model = LLMConfig.create_llm(model_name, self.callback_manager)
        
        # Store the retriever directly
        self.retriever = hybrid_retriever
        
        # Load prompts from files
        self.prompts = self._load_prompts()
        
        # Build the workflow
        self.workflow = StateGraph(MessagesState)
        self.graph = self._build_workflow()
    
    def _load_prompts(self):
        """Load all prompts from text files"""
        prompts = {}
        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        
        # Load grade prompt
        with open(os.path.join(prompts_dir, "grade.txt"), "r") as f:
            prompts["grade"] = f.read().strip()
        
        # Load rewrite prompt
        with open(os.path.join(prompts_dir, "rewrite.txt"), "r") as f:
            prompts["rewrite"] = f.read().strip()
        
        # Load generate prompt
        with open(os.path.join(prompts_dir, "generate.txt"), "r") as f:
            prompts["generate"] = f.read().strip()
        
        return prompts
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = self.workflow
        
        # Define the nodes
        workflow.add_node(self.process_user_query)
        workflow.add_node(self.retrieve_documents)
        workflow.add_node(self.rewrite_question)
        workflow.add_node(self.generate_answer)
        
        # Set up edges
        workflow.add_edge(START, "process_user_query")
        workflow.add_edge("process_user_query", "retrieve_documents")
        
        # Conditional edges after retrieval
        workflow.add_conditional_edges(
            "retrieve_documents",
            self.grade_documents,
            {
                "generate_answer": "generate_answer",
                "rewrite_question": "rewrite_question"
            }
        )
        
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
        except Exception as e:
            logger.error(f"Error generating Mermaid diagram: {str(e)}")
        
        return graph
    
    def process_user_query(self, state: MessagesState):
        """Process the user query for retrieval"""
        # Normalize the query for better processing
        if state["messages"] and len(state["messages"]) > 0:
            query = state["messages"][0].content
            normalized_query = unicodedata.normalize('NFC', query)
            state["messages"][0].content = normalized_query
        return {"messages": state["messages"]}
    
    def retrieve_documents(self, state: MessagesState):
        """Directly retrieve documents using the retriever"""
        query = state["messages"][0].content
        # Get documents from the retriever
        docs = self.retriever.get_relevant_documents(query)
        # Combine document content
        combined_content = "\n\n".join([doc.page_content for doc in docs])
        # Add the retrieved content as a system message
        retrieval_message = AIMessage(content=combined_content)
        # Update the state with the retrieved documents
        return {"messages": state["messages"] + [retrieval_message]}
    
    def grade_documents(self, state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        """Determine whether the retrieved documents are relevant to the question"""
        question = state["messages"][0].content
        context = state["messages"][-1].content
        
        prompt = self.prompts["grade"].format(question=question, context=context)
        
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
        prompt = self.prompts["rewrite"].format(question=question)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": [HumanMessage(content=response.content)]}
    
    def generate_answer(self, state: MessagesState):
        """Generate an answer"""
        question = state["messages"][0].content
        context = state["messages"][-1].content
        prompt = self.prompts["generate"].format(question=question, context=context)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": state["messages"][:-1] + [response]}
    
    def chat(self, message):
        """Process a single chat message and return the response"""
        query = {"messages": [HumanMessage(content=message)]}
        response = self.graph.invoke(query)
        return response["messages"][-1].content
