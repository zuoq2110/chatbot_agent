import io
import os
import sys
import traceback
from typing import List
from typing import Literal

from dotenv import load_dotenv
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import BM25Retriever
from langchain.schema import Document, BaseRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.tools import create_retriever_tool
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langsmith import Client
from pydantic import Field, BaseModel

# Set UTF-8 encoding for stdout and stdin
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# Initialize LangSmith client
langsmith_client = Client()

# Initialize callback manager with LangSmith tracer
callback_manager = CallbackManager([LangChainTracer(project_name="KMARegulation")])


class HybridRetriever(BaseRetriever, BaseModel):
    """Custom hybrid retriever combining BM25 and Vector search with reranking"""
    vectorstore: FAISS = Field(description="FAISS vector store")
    bm25_retriever: BM25Retriever = Field(description="BM25 retriever")
    k: int = Field(default=4, description="Number of documents to retrieve")

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents using hybrid search and reranking"""
        # Get documents from both retrievers
        vector_docs = self.vectorstore.similarity_search(query, k=self.k)
        bm25_docs = self.bm25_retriever.get_relevant_documents(query)

        # Combine unique documents
        all_docs = []
        seen_content = set()

        for doc in vector_docs + bm25_docs:
            if doc.page_content not in seen_content:
                all_docs.append(doc.page_content)
                seen_content.add(doc.page_content)

        print("--" * 50)

        # Convert back to Documents
        return [Document(page_content=content) for content in all_docs]

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """Async version of get_relevant_documents"""
        raise NotImplementedError("Async retrieval not implemented")


def create_vector_database(output_path,
                           data_path="../../../data/regulation.txt"):
    """Create and save the vector database"""
    try:
        # Load the regulation document with UTF-8 encoding
        with open(data_path, "r", encoding="utf-8") as f:
            regulations = f.read()

        # Split the text into chunks with Vietnamese-aware settings
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=200, length_function=len,
            separators=["\n\n", "\n", " ", ""],  # Prioritize natural breaks
            keep_separator=False)
        chunks = text_splitter.split_text(regulations)

        # Create embeddings using Linq-Embed-Mistral
        embeddings = OllamaEmbeddings(model="nomic-embed-text")

        # Create vector store
        vectorstore = FAISS.from_texts(chunks, embeddings)

        if os.path.dirname(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        else:
            os.makedirs(output_path, exist_ok=True)

        vectorstore.save_local(output_path)
        return chunks
    except UnicodeDecodeError as e:
        print(f"Error reading file: {e}")
        raise
    except Exception as e:
        print(f"Error creating vector database: {e}")
        raise


def load_vector_database(output_path):
    """Load the vector database"""
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        if not os.path.exists(output_path):
            chunks = create_vector_database(output_path)
        else:
            # If vector database exists, we still need to get the chunks
            with open(
                    "../../../data/regulation.txt",
                    "r", encoding="utf-8") as f:
                regulations = f.read()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=200, length_function=len,
                separators=["\n\n", "\n", " ", ""], keep_separator=False)
            chunks = text_splitter.split_text(regulations)

        print("Loading vector database...")

        return FAISS.load_local(output_path, embeddings, allow_dangerous_deserialization=True), chunks
    except UnicodeDecodeError as e:
        print(f"Error reading file: {e}")
        raise
    except Exception as e:
        print(f"Error loading vector database: {e}")
        raise


vectorstore, documents = load_vector_database("vector_db")

# Initialize BM25 retriever
bm25_retriever = BM25Retriever.from_texts(texts=documents, k=15)

# Create hybrid retriever with reranking
hybrid_retriever = HybridRetriever(vectorstore=vectorstore, bm25_retriever=bm25_retriever, k=15)

retriever_tool = create_retriever_tool(hybrid_retriever, name="KMARegulationRetriever",
    description="A tool to retrieve information from KMA regulations and rules.", )

llm = ChatOllama(model="llama3.2")


def generate_query_or_respond(state: MessagesState):
    # Initialize LLM
    ai = llm.bind_tools([retriever_tool])
    response = ai.invoke(state["messages"])
    return {"messages": [response]}


GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question that all in vietnamese or another language. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.")


class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(description="Relevance score: 'yes' if relevant, or 'no' if not relevant")


grader_model = ChatOllama(model="llama3.2")


def grade_documents(state: MessagesState, ) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)

    response = (grader_model.with_structured_output(GradeDocuments).invoke([{"role": "user", "content": prompt}]))
    score = response.binary_score

    if score == "yes":
        return "generate_answer"
    else:
        return "rewrite_question"


REWRITE_PROMPT = ("Look at the input and try to reason about the underlying semantic intent / meaning.\n"
                  "Here is the initial question:"
                  "\n ------- \n"
                  "{question}"
                  "\n ------- \n"
                  "Please write only improved question without another words or informations. Formulate an improved question:")


def rewrite_question(state: MessagesState):
    """Rewrite the original user question."""
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [{"role": "user", "content": response.content}]}


GENERATE_PROMPT = ("""
    Bạn là một trợ lý ảo dành cho sinh viên và giảng viên của Học viện Kỹ thuật mật mã (viết tắt là KMA).
    Bạn có hiểu biết về tất cả các quy định và chính sách của trường và có thể giúp đỡ với bất kỳ câu hỏi nào về chúng.
    Bạn sẽ dựa trên thông tin từ tài liệu được cung cấp bên dưới để trả lời câu hỏi của người dùng.
    Hãy trả lời các câu hỏi dưới vai trò một trợ lý ảo thông minh và chuyên nghiệp. Trả lời chính xác và đầy đủ thông tin.
    Nếu không thể trả lời, hãy nói rằng bạn không thể trả lời câu hỏi đó.
    Hãy trả lời các câu hỏi bằng tiếng Việt
    """
                   "Question: {question} \n"
                   "Context: {context}")


def generate_answer(state: MessagesState):
    """Generate an answer."""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}


workflow = StateGraph(MessagesState)

# Define the nodes we will cycle between
workflow.add_node(generate_query_or_respond)
workflow.add_node("retrieve", ToolNode([retriever_tool]))
workflow.add_node(rewrite_question)
workflow.add_node(generate_answer)

workflow.add_edge(START, "generate_query_or_respond")

# Decide whether to retrieve
workflow.add_conditional_edges("generate_query_or_respond",
    # Assess LLM decision (call `retriever_tool` tool or respond to the user)
    tools_condition, {# Translate the condition outputs to nodes in our graph
        "tools": "retrieve", END: END, }, )

# Edges taken after the `action` node is called.
workflow.add_conditional_edges("retrieve", # Assess agent decision
    grade_documents, )
workflow.add_edge("generate_answer", END)
workflow.add_edge("rewrite_question", "generate_query_or_respond")

# Compile
graph = workflow.compile()


def main():
    """Main function to run the chat application"""
    print("Initializing KMA Chat Assistant...")
    try:
        print("\nKMA Chat Assistant is ready! Type 'quit' to exit.")
        print("Ask me anything about KMA!\n")

        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()

                # Check if user wants to quit
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nGoodbye! Have a great day!")
                    break

                # Skip empty inputs
                if not user_input:
                    continue

                # Get AI response
                print("\nAssistant: ", end="")

                query = {"messages": [{"role": "user", "content": user_input, }]}

                response = graph.invoke(query)
                print(response["messages"][-1].content)

            except UnicodeDecodeError as e:
                print(f"\nError with text encoding: {e}")
                print("Please try again with different text.")
            except Exception as e:
                print("\nError during conversation:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print("\nDetailed error traceback:")
                traceback.print_exc()
                print("\nYou can continue chatting or type 'quit' to exit.")

    except Exception as e:
        print("\nFatal error during initialization:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nDetailed error traceback:")
        traceback.print_exc()
        print("\nPlease check your environment setup and try again.")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print("\nUnexpected error:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nDetailed error traceback:")
        traceback.print_exc()
        sys.exit(1)
