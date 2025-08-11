import io
import os
import sys
from typing import List, Optional

from langchain.retrievers import BM25Retriever
from langchain.schema import Document, BaseRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from pydantic import Field, BaseModel
from llm.config import get_gemini_llm

# Set UTF-8 encoding for stdout and stdin
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')


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

        # Convert back to Documents
        return [Document(page_content=content) for content in all_docs]

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """Async version of get_relevant_documents"""
        raise NotImplementedError("Async retrieval not implemented")


def create_vector_database(output_path, data_path="./data/regulation.txt"):
    """Create and save the vector database"""
    try:
        # Load the regulation document with UTF-8 encoding
        with open(data_path, "r", encoding="utf-8") as f:
            regulations = f.read()

        # Split the text into chunks with Vietnamese-aware settings
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400, 
            chunk_overlap=200, 
            length_function=len,
            separators=["\n\n", "\n", " ", ""],  # Prioritize natural breaks
            keep_separator=False
        )
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


def load_vector_database(output_path, data_path="./data/regulation.txt"):
    """Load the vector database"""
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        if not os.path.exists(output_path):
            chunks = create_vector_database(output_path, data_path)
        else:
            # If vector database exists, we still need to get the chunks
            with open(data_path, "r", encoding="utf-8") as f:
                regulations = f.read()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=400, 
                chunk_overlap=200, 
                length_function=len,
                separators=["\n\n", "\n", " ", ""], 
                keep_separator=False
            )
            chunks = text_splitter.split_text(regulations)

        print("Loading vector database...")

        return FAISS.load_local(output_path, embeddings, allow_dangerous_deserialization=True), chunks
    except UnicodeDecodeError as e:
        print(f"Error reading file: {e}")
        raise
    except Exception as e:
        print(f"Error loading vector database: {e}")
        raise


def create_hybrid_retriever(vector_db_path, data_path="./data/regulation.txt"):
    """Create a hybrid retriever combining vector search and BM25"""
    vectorstore, documents = load_vector_database(vector_db_path, data_path)
    
    # Initialize BM25 retriever
    bm25_retriever = BM25Retriever.from_texts(texts=documents, k=15)
    
    # Create hybrid retriever with reranking
    return HybridRetriever(
        vectorstore=vectorstore, 
        bm25_retriever=bm25_retriever, 
        k=15
    ), documents 