# KMA RAG Chatbot - Agentic RAG and Backend

# Agentic RAG

An intelligent chatbot for answering questions about regulations at the Academy of Cryptographic Techniques (KMA). This project uses LangChain, LangGraph, and Ollama to provide accurate responses to user queries about KMA's regulations.

## Features
- **Hybrid Retrieval**: Combines vector search (FAISS) and keyword search (BM25) for optimal information retrieval
- **Intelligent Rewriting**: Improves queries that don't initially match relevant documents
- **Relevance Grading**: Evaluates document relevance to ensure accurate responses
- **Streamlit UI for test**: Clean Streamlit interface for easy interaction
- **Multi-language Support**: Fully supports Vietnamese language for both queries and responses

## Mermaid Diagram

```mermaid
graph TD;
        __start__([<p>__start__</p>]):::first
        process_user_query(process_user_query)
        retrieve_documents(retrieve_documents)
        rewrite_question(rewrite_question)
        generate_answer(generate_answer)
        __end__([<p>__end__</p>]):::last
        __start__ --> process_user_query;
        generate_answer --> __end__;
        process_user_query --> retrieve_documents;
        rewrite_question --> process_user_query;
        retrieve_documents -.-> generate_answer;
        retrieve_documents -.-> rewrite_question;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```

## How to run streamlit app

1. Install the required packages:
   ```bash
   poetry install
   ```
2. Activate the virtual environment:
   ```bash
   poetry env activate
   ```
   
3. Run the Streamlit app:
   ```bash
     streamlit run src/rag/streamlit_app.py 
    ```

