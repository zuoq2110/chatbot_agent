import glob
import os
import io
import sys
from typing import List
from langchain.retrievers import BM25Retriever
from langchain.schema import Document, BaseRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from pydantic import Field, BaseModel

# Set UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')


class HybridRetriever(BaseRetriever, BaseModel):
    vectorstore: FAISS = Field(description="FAISS vector store")
    bm25_retriever: BM25Retriever = Field(description="BM25 retriever")
    k: int = Field(default=4, description="Number of documents to retrieve")

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str) -> List[Document]:
        vector_docs = self.vectorstore.similarity_search(query, k=self.k)
        bm25_docs = self.bm25_retriever.get_relevant_documents(query)

        all_docs = []
        seen_content = set()
        for doc in vector_docs + bm25_docs:
            if doc.page_content not in seen_content:
                all_docs.append(doc.page_content)
                seen_content.add(doc.page_content)

        return [Document(page_content=content) for content in all_docs]

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        raise NotImplementedError("Async retrieval not implemented")


def read_all_text_files(data_dir):
    """Đọc toàn bộ nội dung các file .txt trong thư mục"""
    combined_text = ""
    for file_path in glob.glob(os.path.join(data_dir, "*.txt")):
        with open(file_path, "r", encoding="utf-8") as f:
            combined_text += f.read() + "\n\n"
    return combined_text


def create_vector_database(output_path, data_dir="./data"):
    try:
        regulations = read_all_text_files(data_dir)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400, 
            chunk_overlap=200, 
            length_function=len,
            separators=["\n\n", "\n", " ", ""],  
            keep_separator=False
        )
        chunks = text_splitter.split_text(regulations)

        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://172.17.0.1:11434"
        )

        vectorstore = FAISS.from_texts(chunks, embeddings)

        if os.path.dirname(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        else:
            os.makedirs(output_path, exist_ok=True)

        vectorstore.save_local(output_path)
        return chunks
    except Exception as e:
        print(f"Error creating vector database: {e}")
        raise


def load_vector_database(output_path, data_dir="./data"):
    try:
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://172.17.0.1:11434"
        )

        if not os.path.exists(output_path):
            chunks = create_vector_database(output_path, data_dir)
        else:
            regulations = read_all_text_files(data_dir)
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
    except Exception as e:
        print(f"Error loading vector database: {e}")
        raise


def create_hybrid_retriever(vector_db_path, data_dir="./data"):
    vectorstore, documents = load_vector_database(vector_db_path, data_dir)
    bm25_retriever = BM25Retriever.from_texts(texts=documents, k=15)

    return HybridRetriever(
        vectorstore=vectorstore, 
        bm25_retriever=bm25_retriever, 
        k=15
    ), documents
