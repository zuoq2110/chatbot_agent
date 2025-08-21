"""
API endpoints for managing RAG training data

This module provides API endpoints for uploading files to the data directory
for RAG training, listing available training files, and deleting training files.
"""
import logging
import os
import sys
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException, Body, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.auth.jwt import get_current_user
from backend.models.user import UserResponse
from rag.retriever import extract_text_from_file

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Define the data directory path
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data"))
VECTOR_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "vector_db"))

# Ensure directories exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logger.info(f"Created data directory at {DATA_DIR}")
    
if not os.path.exists(VECTOR_DB_PATH):
    os.makedirs(VECTOR_DB_PATH)
    logger.info(f"Created vector database directory at {VECTOR_DB_PATH}")

class FileInfo(BaseModel):
    """Model for file information"""
    filename: str
    size: int
    last_modified: str
    path: str

@router.post("/upload-training-file", response_model=Dict[str, Any])
async def upload_training_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a file to the data directory for RAG training
    
    This endpoint allows administrators to upload documents for RAG training.
    Supported file types include PDF, DOCX, TXT.
    
    Returns:
        A dictionary with file information
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can upload training files")
    
    try:
        # Log file upload attempt
        logger.info(f"Uploading training file: {file.filename}, Content-Type: {file.content_type}")
        
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Ensure only allowed file types
        allowed_extensions = ['.txt', '.pdf', '.docx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Please upload files with these extensions: {', '.join(allowed_extensions)}"
            )
        
        # Use original filename for simplicity in this version
        safe_filename = file.filename
        file_path = os.path.join(DATA_DIR, safe_filename)
        
        # Log the file path
        logger.info(f"Saving file to: {file_path}")
        
        # Save the file to the data directory
        with open(file_path, "wb") as f:
            f.write(content)
        
        # For non-text files, also create a text version for easy viewing/processing
        if file_ext != '.txt':
            try:
                logger.info(f"Extracting text from {file.filename} with content type {file.content_type}")
                text_content = extract_text_from_file(file_path, file.content_type)
                
                if text_content.startswith("Error") or text_content.startswith("Unsupported"):
                    logger.warning(f"Problem extracting text: {text_content}")
                else:
                    text_file_path = os.path.splitext(file_path)[0] + ".txt"
                    with open(text_file_path, "w", encoding="utf-8") as f:
                        f.write(text_content)
                    logger.info(f"Extracted text saved to {text_file_path}")
            except Exception as e:
                logger.warning(f"Could not extract text from {file.filename}: {str(e)}")
        
        file_size = os.path.getsize(file_path)
        
        logger.info(f"Training file uploaded successfully: {safe_filename}, Size: {file_size} bytes")
        
        # Trả về kết quả mà không rebuild index
        return {
            "success": True,
            "fileInfo": {
                "filename": safe_filename,
                "originalName": file.filename,
                "size": file_size,
                "uploadedBy": current_user["username"],
                "uploadTime": str(datetime.now())
            },
            "message": "File uploaded successfully. Please use the 'Rebuild RAG Index' function to update the knowledge base."
        }
    
    except Exception as e:
        logger.error(f"Error processing training file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/list-training-files", response_model=Dict[str, Any])
async def list_training_files(current_user: dict = Depends(get_current_user)):
    """
    List all files in the data directory for RAG training
    
    This endpoint allows administrators to view all available training files.
    
    Returns:
        A response containing a list of file information
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can view training files")
    
    try:
        file_list = []
        
        # Ensure data directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logger.info(f"Created data directory at {DATA_DIR}")
            return {
                "success": True,
                "files": [],
                "count": 0,
                "message": "Data directory was empty and has been created"
            }
        
        for filename in os.listdir(DATA_DIR):
            file_path = os.path.join(DATA_DIR, filename)
            if os.path.isfile(file_path):
                # Skip .gitkeep and other hidden files
                if filename.startswith('.'):
                    continue
                    
                file_stat = os.stat(file_path)
                file_list.append({
                    "filename": filename,
                    "size": file_stat.st_size,
                    "last_modified": str(datetime.fromtimestamp(file_stat.st_mtime)),
                    "path": file_path
                })
        
        logger.info(f"Found {len(file_list)} files in the data directory")
        
        return {
            "success": True,
            "files": file_list,
            "count": len(file_list)
        }
    
    except Exception as e:
        logger.error(f"Error listing training files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.delete("/delete-training-file/{filename}", response_model=Dict[str, Any])
async def delete_training_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a file from the data directory
    
    This endpoint allows administrators to delete training files.
    
    Args:
        filename: The name of the file to delete
        
    Returns:
        A response indicating success or failure
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete training files")
    
    try:
        file_path = os.path.join(DATA_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        # Delete the file
        os.remove(file_path)
        
        # Also delete the text version if it exists
        text_file_path = os.path.splitext(file_path)[0] + ".txt"
        if os.path.exists(text_file_path):
            os.remove(text_file_path)
            logger.info(f"Deleted text version: {text_file_path}")
        
        logger.info(f"Training file deleted: {filename}")
        
        return {
            "success": True,
            "message": f"File '{filename}' deleted successfully. Please use the 'Rebuild RAG Index' function to update the knowledge base.",
            "filename": filename
        }
    
    except Exception as e:
        logger.error(f"Error deleting training file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.post("/rebuild-rag-index", response_model=Dict[str, Any])
async def rebuild_rag_index(current_user: dict = Depends(get_current_user)):
    """
    Rebuild the RAG vector index from the current data directory
    
    This endpoint triggers a rebuild of the RAG vector index after files 
    have been added or removed.
    
    Returns:
        A response indicating success or failure
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can rebuild the RAG index")
    
    try:
        from rag.retriever import create_vector_database
        
        # Path to vector database
        vector_db_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
            "vector_db"
        ))
        
        logger.info(f"Rebuilding RAG index from data directory: {DATA_DIR}")
        logger.info(f"Saving vector database to: {vector_db_path}")
        
        # Rebuild the vector database
        chunks = create_vector_database(vector_db_path, DATA_DIR)
        
        logger.info(f"RAG index rebuilt successfully with {len(chunks)} chunks")
        
        return {
            "success": True,
            "message": f"RAG index rebuilt successfully with {len(chunks)} chunks",
            "chunks": len(chunks)
        }
    
    except Exception as e:
        logger.error(f"Error rebuilding RAG index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error rebuilding RAG index: {str(e)}")
