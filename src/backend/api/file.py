"""
API endpoints for file upload and queries

This module provides API endpoints for uploading files, querying files,
and getting information about uploaded files. The uploaded files are stored
in memory temporarily and can be queried using a generated file_id.
"""
import logging
import os
import sys
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add the parent directory to sys.path to import our agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag.retriever import extract_text_from_file, create_in_memory_retriever
from rag.simple_chat_agent import SimpleChatAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Store uploaded files and their retrievers in memory temporarily
uploaded_files = {}

class QueryRequest(BaseModel):
    """Request model for querying a file"""
    file_id: str = Field(..., description="ID of the uploaded file to query")
    query: str = Field(..., description="The query to run against the file")

class MultiQueryRequest(BaseModel):
    """Request model for querying a file with multiple questions"""
    file_id: str = Field(..., description="ID of the uploaded file to query")
    queries: List[str] = Field(..., description="List of queries to run against the file")

@router.post("/upload-file", response_model=Dict[str, Any])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and create a retriever for it
    
    This endpoint allows uploading documents for question answering.
    Supported file types include PDF, DOCX, TXT, and more.
    
    Returns:
        A dictionary with file information including a unique file_id
        that can be used for querying the file later.
    """
    try:
        # Log file upload attempt
        logger.info(f"Uploading file: {file.filename}, Content-Type: {file.content_type}")
        
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
            
        # Create a temporary file
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Extract text from file
        file_content = extract_text_from_file(temp_path, file.content_type)
        
        # Remove temporary file
        os.unlink(temp_path)
        
        if file_content.startswith("Error") or file_content.startswith("Unsupported"):
            logger.error(f"File processing error: {file_content}")
            raise HTTPException(status_code=400, detail=file_content)
        
        # Create retriever for file content
        retriever, chunks = create_in_memory_retriever(file_content)
        
        # Generate unique file ID
        file_id = f"file_{hash(file.filename)}_{hash(file_content[:100])}"
        
        # Store retriever in memory
        uploaded_files[file_id] = {
            "filename": file.filename,
            "retriever": retriever,
            "content": file_content,
            "chunks": chunks,
            "upload_time": str(datetime.now()),
            "content_type": file.content_type
        }
        
        logger.info(f"File uploaded successfully: {file.filename}, ID: {file_id}, Chunks: {len(chunks)}")
        
        return {
            "success": True,
            "fileInfo": {
                "id": file_id,
                "filename": file.filename,
                "size": len(file_content),
                "chunks": len(chunks),
                "content_type": file.content_type
            }
        }
    
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/query-file", response_model=Dict[str, Any])
async def query_file(request: QueryRequest):
    """
    Query a specific uploaded file
    
    This endpoint allows you to ask questions about a previously uploaded file.
    
    Args:
        request: QueryRequest object containing file_id and query
        
    Returns:
        A response containing the answer to the query and relevant source context
    """
    try:
        file_id = request.file_id
        query = request.query
        
        logger.info(f"Querying file ID: {file_id}, Query: {query}")
        
        # Check if file exists
        if file_id not in uploaded_files:
            logger.warning(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail="File not found. It may have expired.")
        
        # Get retriever for file
        file_data = uploaded_files[file_id]
        retriever = file_data["retriever"]
        
        # Create agent with file retriever
        agent = SimpleChatAgent(custom_retriever=retriever)
        
        # Process query
        answer = agent.chat(query)
        
        # Get sources for context
        docs = retriever.get_relevant_documents(query)
        sources = [doc.page_content for doc in docs[:3]]
        
        logger.info(f"Query processed successfully for file: {file_data['filename']}")
        
        return {
            "success": True,
            "answer": answer,
            "sources": sources,
            "file": {
                "id": file_id,
                "filename": file_data["filename"],
                "total_chunks": len(file_data["chunks"])
            },
            "timestamp": str(datetime.now())
        }
    
    except Exception as e:
        logger.error(f"Error processing file query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/multi-query-file", response_model=Dict[str, Any])
async def multi_query_file(request: MultiQueryRequest):
    """
    Run multiple queries against a single file
    
    This endpoint allows you to ask multiple questions about a previously uploaded file
    in a single request.
    
    Args:
        request: MultiQueryRequest object containing file_id and a list of queries
        
    Returns:
        A response containing answers to all queries with their relevant source contexts
    """
    try:
        file_id = request.file_id
        queries = request.queries
        
        if not queries:
            raise HTTPException(status_code=400, detail="No queries provided")
            
        logger.info(f"Multi-querying file ID: {file_id}, Queries: {len(queries)}")
        
        # Check if file exists
        if file_id not in uploaded_files:
            logger.warning(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail="File not found. It may have expired.")
        
        # Get retriever for file
        file_data = uploaded_files[file_id]
        retriever = file_data["retriever"]
        
        # Create agent with file retriever
        agent = SimpleChatAgent(custom_retriever=retriever)
        
        # Process all queries
        results = []
        for query in queries:
            # Process query
            answer = agent.chat(query)
            
            # Get sources for context
            docs = retriever.get_relevant_documents(query)
            sources = [doc.page_content for doc in docs[:2]]  # Limit to 2 sources per query
            
            results.append({
                "query": query,
                "answer": answer,
                "sources": sources
            })
        
        logger.info(f"Multi-query processed successfully for file: {file_data['filename']}")
        
        return {
            "success": True,
            "results": results,
            "file": {
                "id": file_id,
                "filename": file_data["filename"],
            },
            "timestamp": str(datetime.now())
        }
    
    except Exception as e:
        logger.error(f"Error processing multi-file query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing queries: {str(e)}")

@router.get("/file-info/{file_id}", response_model=Dict[str, Any])
async def get_file_info(file_id: str):
    """
    Get information about an uploaded file
    
    This endpoint returns details about a previously uploaded file.
    
    Args:
        file_id: The ID of the file to get information about
        
    Returns:
        A response containing information about the file
    """
    if file_id not in uploaded_files:
        logger.warning(f"File info requested for non-existent file: {file_id}")
        raise HTTPException(status_code=404, detail="File not found. It may have expired.")
    
    file_data = uploaded_files[file_id]
    
    # Get the first few chunks as preview
    preview_chunks = file_data["chunks"][:3]
    preview_text = "\n".join([chunk.page_content for chunk in preview_chunks]) if preview_chunks else ""
    # Limit preview text to 500 characters
    preview_text = preview_text[:500] + "..." if len(preview_text) > 500 else preview_text
    
    return {
        "success": True,
        "fileInfo": {
            "id": file_id,
            "filename": file_data["filename"],
            "size": len(file_data["content"]),
            "chunks": len(file_data["chunks"]),
            "content_type": file_data.get("content_type", "unknown"),
            "upload_time": file_data.get("upload_time", "unknown"),
            "preview": preview_text
        }
    }

@router.get("/list-files", response_model=Dict[str, Any])
async def list_files():
    """
    List all uploaded files
    
    This endpoint returns a list of all files that have been uploaded
    and are still available for querying.
    
    Returns:
        A response containing a list of file information
    """
    file_list = []
    for file_id, file_data in uploaded_files.items():
        file_list.append({
            "id": file_id,
            "filename": file_data["filename"],
            "size": len(file_data["content"]),
            "chunks": len(file_data["chunks"]),
            "content_type": file_data.get("content_type", "unknown"),
            "upload_time": file_data.get("upload_time", "unknown")
        })
    
    return {
        "success": True,
        "files": file_list,
        "count": len(file_list)
    }

@router.delete("/delete-file/{file_id}", response_model=Dict[str, Any])
async def delete_file(file_id: str):
    """
    Delete an uploaded file
    
    This endpoint removes a file from memory, freeing up resources.
    
    Args:
        file_id: The ID of the file to delete
        
    Returns:
        A response indicating success or failure
    """
    if file_id not in uploaded_files:
        logger.warning(f"Delete requested for non-existent file: {file_id}")
        raise HTTPException(status_code=404, detail="File not found. It may have expired.")
    
    file_data = uploaded_files[file_id]
    filename = file_data["filename"]
    
    # Remove the file from memory
    del uploaded_files[file_id]
    
    logger.info(f"File deleted: {filename}, ID: {file_id}")
    
    return {
        "success": True,
        "message": f"File '{filename}' deleted successfully",
        "file_id": file_id
    }
