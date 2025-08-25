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

from fastapi import APIRouter, File, UploadFile, HTTPException, Body, Query, Depends, Path
from fastapi.responses import JSONResponse, FileResponse
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

class FolderRequest(BaseModel):
    """Request model for creating a folder"""
    folder_name: str = Field(..., description="Name of the folder to create")

class SubfolderRequest(BaseModel):
    """Request model for creating a subfolder"""
    parent_folder: str = Field(..., description="Name of the parent folder")
    subfolder_name: str = Field(..., description="Name of the subfolder to create")

class FolderRenameRequest(BaseModel):
    """Request model for renaming a folder"""
    old_name: str = Field(..., description="Current name of the folder")
    new_name: str = Field(..., description="New name for the folder")

@router.post("/upload-training-file", response_model=Dict[str, Any])
async def upload_training_file(
    file: UploadFile = File(...),
    folder: str = Query("default", description="Folder to store the file in"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a file to the data directory for RAG training
    
    This endpoint allows administrators to upload documents for RAG training.
    Supported file types include PDF, DOCX, TXT.
    
    Args:
        file: The file to upload
        folder: The folder to store the file in (default: "default")
        
    Returns:
        A dictionary with file information
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can upload training files")
    
    try:
        # Log file upload attempt
        logger.info(f"Uploading training file: {file.filename}, Content-Type: {file.content_type}, to folder: {folder}")
        
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
        
        # Determine folder path
        if folder == "default":
            folder_path = DATA_DIR
        else:
            # Xử lý subfolder
            if "/" in folder:
                # Đây là subfolder, cần xử lý đường dẫn đặc biệt
                folder_parts = folder.split("/")
                # Bắt đầu từ DATA_DIR và xây dựng đường dẫn dựa trên các phần của folder
                current_path = DATA_DIR
                for part in folder_parts:
                    current_path = os.path.join(current_path, part)
                folder_path = current_path
            else:
                # Đây là folder thông thường
                folder_path = os.path.join(DATA_DIR, folder)
            
            # Create folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                logger.info(f"Created folder: {folder_path}")
        
        # Use original filename for simplicity in this version
        safe_filename = file.filename
        file_path = os.path.join(folder_path, safe_filename)
        
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
        
        # Function to get files from a folder
        def get_files_from_folder(folder_path, folder_name="default"):
            folder_files = []
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        # Skip .gitkeep and other hidden files
                        if filename.startswith('.'):
                            continue
                            
                        file_stat = os.stat(file_path)
                        folder_files.append({
                            "filename": filename,
                            "folder": folder_name,
                            "size": file_stat.st_size,
                            "last_modified": str(datetime.fromtimestamp(file_stat.st_mtime)),
                            "path": file_path
                        })
                    # Đệ quy xuống các subfolder
                    elif os.path.isdir(file_path) and filename != "__pycache__":
                        subfolder_name = f"{folder_name}/{filename}" if folder_name != "default" else filename
                        folder_files.extend(get_files_from_folder(file_path, subfolder_name))
            return folder_files
        
        # Get files from default folder (DATA_DIR)
        file_list.extend(get_files_from_folder(DATA_DIR))
        
        # Chúng ta không cần đoạn mã dưới đây vì hàm get_files_from_folder đã được cập nhật
        # để duyệt qua tất cả các subfolder một cách đệ quy
        # for item in os.listdir(DATA_DIR):
        #     item_path = os.path.join(DATA_DIR, item)
        #     if os.path.isdir(item_path) and item != "__pycache__":
        #         file_list.extend(get_files_from_folder(item_path, item))
        
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
    folder: str = Query("default", description="Folder containing the file"),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a file from the data directory
    
    This endpoint allows administrators to delete training files.
    
    Args:
        filename: The name of the file to delete
        folder: The folder containing the file (default: "default")
        
    Returns:
        A response indicating success or failure
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete training files")
    
    try:
        # Determine folder path
        if folder == "default":
            folder_path = DATA_DIR
        else:
            # Xử lý subfolder
            if "/" in folder:
                # Đây là subfolder, cần xử lý đường dẫn đặc biệt
                folder_parts = folder.split("/")
                # Bắt đầu từ DATA_DIR và xây dựng đường dẫn dựa trên các phần của folder
                current_path = DATA_DIR
                for part in folder_parts:
                    current_path = os.path.join(current_path, part)
                folder_path = current_path
            else:
                # Đây là folder thông thường
                folder_path = os.path.join(DATA_DIR, folder)
            
        file_path = os.path.join(folder_path, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found in folder {folder}")
        
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
        
        # Tải lại ReActGraph để sử dụng chỉ mục mới
        from backend.api.chat import agent
        from agent.supervisor_agent import ReActGraph
        
        # Khởi tạo lại agent với chỉ mục mới
        new_agent = ReActGraph()
        new_agent.create_graph()
        
        # Gán lại biến toàn cục agent trong module chat
        import backend.api.chat
        backend.api.chat.agent = new_agent
        
        logger.info("ReActGraph agent reinitialized with new index")
        
        return {
            "success": True,
            "message": f"RAG index rebuilt successfully with {len(chunks)} chunks",
            "chunks": len(chunks)
        }
    
    except Exception as e:
        logger.error(f"Error rebuilding RAG index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error rebuilding RAG index: {str(e)}")

# Folder Management Endpoints
@router.get("/list-folders", response_model=Dict[str, Any])
async def list_folders(current_user: dict = Depends(get_current_user)):
    """
    List all folders in the data directory
    
    Returns:
        A response containing a list of folders
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can list folders")
        
    try:
        # Get list of subdirectories in DATA_DIR
        folders = ["default"]  # Always include default
        
        # Function to scan all subfolders
        def scan_folders(directory, parent_path=""):
            folder_list = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path) and item != "__pycache__":
                    folder_name = item
                    if parent_path:
                        folder_name = f"{parent_path}/{item}"
                    folder_list.append(folder_name)
                    # Scan subfolders
                    folder_list.extend(scan_folders(item_path, folder_name))
            return folder_list
                
        # Get all folders including subfolders
        folders.extend(scan_folders(DATA_DIR))
                
        return {
            "success": True,
            "folders": folders,
            "count": len(folders)
        }
    except Exception as e:
        logger.error(f"Error listing folders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing folders: {str(e)}")

@router.post("/create-folder", response_model=Dict[str, Any])
async def create_folder(request: FolderRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new folder in the data directory
    
    Args:
        request: FolderRequest containing folder_name
        
    Returns:
        A response indicating success or failure
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can create folders")
        
    folder_name = request.folder_name.strip()
    
    if not folder_name:
        raise HTTPException(status_code=400, detail="Folder name cannot be empty")
        
    folder_path = os.path.join(DATA_DIR, folder_name)
    
    if os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail=f"Folder '{folder_name}' already exists")
        
    try:
        os.makedirs(folder_path)
        logger.info(f"Created folder: {folder_path}")
        
        return {
            "success": True,
            "message": f"Folder '{folder_name}' created successfully",
            "folder_name": folder_name
        }
    except Exception as e:
        logger.error(f"Error creating folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating folder: {str(e)}")

@router.delete("/delete-folder/{folder_name:path}", response_model=Dict[str, Any])
async def delete_folder(folder_name: str, delete_files: bool = Query(True), current_user: dict = Depends(get_current_user)):
    """
    Delete a folder from the data directory
    
    Args:
        folder_name: The name of the folder to delete (can include path for subfolders)
        delete_files: Whether to delete the files in the folder
        
    Returns:
        A response indicating success or failure
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete folders")
        
    if folder_name == "default":
        raise HTTPException(status_code=400, detail="Cannot delete the default folder")
        
    # Xử lý subfolder
    if "/" in folder_name:
        # Đây là subfolder, cần xử lý đường dẫn đặc biệt
        folder_parts = folder_name.split("/")
        # Bắt đầu từ DATA_DIR và xây dựng đường dẫn dựa trên các phần của folder
        current_path = DATA_DIR
        for part in folder_parts:
            current_path = os.path.join(current_path, part)
        folder_path = current_path
    else:
        # Đây là folder thông thường
        folder_path = os.path.join(DATA_DIR, folder_name)
    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail=f"Folder '{folder_name}' not found")
        
    try:
        if delete_files:
            # Delete the folder and all its contents
            shutil.rmtree(folder_path)
            logger.info(f"Deleted folder and contents: {folder_path}")
            
            return {
                "success": True,
                "message": f"Folder '{folder_name}' and all its contents deleted successfully"
            }
        else:
            # Move files to default folder and delete the folder
            files_moved = 0
            
            for filename in os.listdir(folder_path):
                src_path = os.path.join(folder_path, filename)
                dst_path = os.path.join(DATA_DIR, filename)
                
                if os.path.isfile(src_path):
                    # If file with same name exists in default, add a suffix
                    if os.path.exists(dst_path):
                        name, ext = os.path.splitext(filename)
                        dst_path = os.path.join(DATA_DIR, f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}")
                    
                    shutil.move(src_path, dst_path)
                    files_moved += 1
            
            # Now delete the empty folder
            os.rmdir(folder_path)
            
            logger.info(f"Moved {files_moved} files to default folder and deleted folder: {folder_path}")
            
            return {
                "success": True,
                "message": f"Moved {files_moved} files to default folder and deleted folder '{folder_name}'"
            }
    except Exception as e:
        logger.error(f"Error deleting folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting folder: {str(e)}")

@router.put("/rename-folder", response_model=Dict[str, Any])
async def rename_folder(request: FolderRenameRequest, current_user: dict = Depends(get_current_user)):
    """
    Rename a folder in the data directory
    
    Args:
        request: FolderRenameRequest containing old_name and new_name
        
    Returns:
        A response indicating success or failure
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can rename folders")
        
    old_name = request.old_name.strip()
    new_name = request.new_name.strip()
    
    if old_name == "default":
        raise HTTPException(status_code=400, detail="Cannot rename the default folder")
        
    if not new_name:
        raise HTTPException(status_code=400, detail="New folder name cannot be empty")
    
    # Xử lý subfolder trong đổi tên
    if "/" in old_name:
        # Đây là subfolder, cần xử lý đường dẫn đặc biệt
        old_folder_parts = old_name.split("/")
        # Bắt đầu từ DATA_DIR và xây dựng đường dẫn dựa trên các phần của folder
        old_path_current = DATA_DIR
        for part in old_folder_parts:
            old_path_current = os.path.join(old_path_current, part)
        old_path = old_path_current
        
        # Xử lý tên mới (giữ nguyên cấu trúc thư mục cha, chỉ đổi tên thư mục con cuối cùng)
        if "/" in new_name:
            # Nếu tên mới có cấu trúc thư mục, sử dụng nó trực tiếp
            new_folder_parts = new_name.split("/")
            new_path_current = DATA_DIR
            for part in new_folder_parts:
                new_path_current = os.path.join(new_path_current, part)
            new_path = new_path_current
        else:
            # Nếu tên mới không có cấu trúc thư mục, giữ nguyên cấu trúc cũ và chỉ thay đổi tên cuối
            parent_folder = "/".join(old_folder_parts[:-1])
            if parent_folder:
                new_folder_parts = parent_folder.split("/")
                new_path_current = DATA_DIR
                for part in new_folder_parts:
                    new_path_current = os.path.join(new_path_current, part)
                new_path = os.path.join(new_path_current, new_name)
            else:
                new_path = os.path.join(DATA_DIR, new_name)
    else:
        # Đây là folder thông thường
        old_path = os.path.join(DATA_DIR, old_name)
        new_path = os.path.join(DATA_DIR, new_name)
    
    if not os.path.exists(old_path) or not os.path.isdir(old_path):
        raise HTTPException(status_code=404, detail=f"Folder '{old_name}' not found")
        
    if os.path.exists(new_path):
        raise HTTPException(status_code=400, detail=f"Folder '{new_name}' already exists")
        
    try:
        os.rename(old_path, new_path)
        logger.info(f"Renamed folder: {old_name} -> {new_name}")
        
        return {
            "success": True,
            "message": f"Folder renamed from '{old_name}' to '{new_name}' successfully"
        }
    except Exception as e:
        logger.error(f"Error renaming folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error renaming folder: {str(e)}")

@router.post("/create-subfolder", response_model=Dict[str, Any])
async def create_subfolder(request: SubfolderRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new subfolder inside an existing folder
    
    Args:
        request: SubfolderRequest containing parent_folder and subfolder_name
        
    Returns:
        A response indicating success or failure
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can create subfolders")
        
    parent_folder = request.parent_folder.strip()
    subfolder_name = request.subfolder_name.strip()
    
    if not parent_folder or not subfolder_name:
        raise HTTPException(status_code=400, detail="Parent folder and subfolder name cannot be empty")
    
    # Determine parent folder path
    if parent_folder == "default":
        parent_path = DATA_DIR
    else:
        parent_path = os.path.join(DATA_DIR, parent_folder)
    
    # Check if parent folder exists
    if not os.path.exists(parent_path) or not os.path.isdir(parent_path):
        raise HTTPException(status_code=404, detail=f"Parent folder '{parent_folder}' not found")
    
    # Create full path for the subfolder
    subfolder_path = os.path.join(parent_path, subfolder_name)
    
    # Check if subfolder already exists
    if os.path.exists(subfolder_path):
        raise HTTPException(status_code=400, detail=f"Subfolder '{subfolder_name}' already exists in '{parent_folder}'")
    
    try:
        # Create the subfolder
        os.makedirs(subfolder_path)
        logger.info(f"Created subfolder: {subfolder_path}")
        
        # Create the full folder path for response
        full_folder_name = parent_folder
        if parent_folder != "default":
            full_folder_name = f"{parent_folder}/{subfolder_name}"
        else:
            full_folder_name = subfolder_name
        
        return {
            "success": True,
            "message": f"Subfolder '{subfolder_name}' created successfully in '{parent_folder}'",
            "folder_name": full_folder_name
        }
    except Exception as e:
        logger.error(f"Error creating subfolder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating subfolder: {str(e)}")

# Thêm endpoint cho download file
@router.get("/download-training-file/{filename}", response_model=None)
async def download_training_file(
    filename: str,
    folder: str = Query("default", description="Folder containing the file"),
    current_user: dict = Depends(get_current_user)
):
    """
    Download a file from the data directory
    
    This endpoint allows administrators to download training files.
    
    Args:
        filename: The name of the file to download
        folder: The folder containing the file (default: "default")
        
    Returns:
        The file content
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can download training files")
    
    try:
        # Determine folder path
        if folder == "default":
            folder_path = DATA_DIR
        else:
            # Xử lý subfolder
            if "/" in folder:
                # Đây là subfolder, cần xử lý đường dẫn đặc biệt
                folder_parts = folder.split("/")
                # Bắt đầu từ DATA_DIR và xây dựng đường dẫn dựa trên các phần của folder
                current_path = DATA_DIR
                for part in folder_parts:
                    current_path = os.path.join(current_path, part)
                folder_path = current_path
            else:
                # Đây là folder thông thường
                folder_path = os.path.join(DATA_DIR, folder)
            
        file_path = os.path.join(folder_path, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found in folder {folder}")
        
        logger.info(f"Downloading file: {file_path}")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path, 
            filename=filename,
            media_type='application/octet-stream'
        )
    
    except Exception as e:
        logger.error(f"Error downloading training file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

# File content model
class FileContentRequest(BaseModel):
    """Request model for updating file content"""
    content: str = Field(..., description="New content for the file")

class EditFileRequest(BaseModel):
    """Request model for editing a file"""
    file_path: str = Field(..., description="Path to the file to edit, can include folder/subfolder")
    content: str = Field(..., description="New content for the file")

# Thêm endpoint cho edit file (chỉ hỗ trợ file text)
@router.get("/get-file-content/{filename}", response_model=Dict[str, Any])
async def get_file_content(
    filename: str,
    folder: str = Query("default", description="Folder containing the file"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the content of a text file from the data directory
    
    This endpoint allows administrators to get the content of a text file for editing.
    Only text files (.txt) are supported.
    
    Args:
        filename: The name of the file to get content from
        folder: The folder containing the file (default: "default")
        
    Returns:
        The file content
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can edit training files")
    
    try:
        # Determine folder path
        if folder == "default":
            folder_path = DATA_DIR
        else:
            # Xử lý subfolder
            if "/" in folder:
                # Đây là subfolder, cần xử lý đường dẫn đặc biệt
                folder_parts = folder.split("/")
                # Bắt đầu từ DATA_DIR và xây dựng đường dẫn dựa trên các phần của folder
                current_path = DATA_DIR
                for part in folder_parts:
                    current_path = os.path.join(current_path, part)
                folder_path = current_path
            else:
                # Đây là folder thông thường
                folder_path = os.path.join(DATA_DIR, folder)
            
        file_path = os.path.join(folder_path, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found in folder {folder}")
        
        # Check if file is a text file
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext != '.txt':
            raise HTTPException(status_code=400, detail="Only text files (.txt) can be edited")
        
        logger.info(f"Getting content of file: {file_path}")
        
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "success": True,
            "filename": filename,
            "folder": folder,
            "content": content
        }
    
    except Exception as e:
        logger.error(f"Error getting file content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting file content: {str(e)}")

@router.put("/edit-file", response_model=Dict[str, Any])
async def update_file_content(
    request: EditFileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update the content of a text file in the data directory
    
    This endpoint allows administrators to update the content of a text file.
    Only text files (.txt) are supported.
    
    Args:
        request: EditFileRequest containing the file path and new content
        
    Returns:
        Success message
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can edit training files")
    
    try:
        path = request.file_path
        
        # Split path into folder and filename
        # If path has no slashes, assume it's a file in the root data directory
        if "/" not in path:
            filename = path
            folder_path = DATA_DIR
        else:
            # Split by last slash to get folder path and filename
            *folder_parts, filename = path.split("/")
            folder = "/".join(folder_parts)
            
            # Determine folder path
            if folder == "default" or not folder:
                folder_path = DATA_DIR
            else:
                # Xây dựng đường dẫn dựa trên các phần của folder
                current_path = DATA_DIR
                for part in folder_parts:
                    current_path = os.path.join(current_path, part)
                folder_path = current_path
                
        file_path = os.path.join(folder_path, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {filename} not found in folder {folder}")
        
        # Check if file is a text file
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext != '.txt':
            raise HTTPException(status_code=400, detail="Only text files (.txt) can be edited")
        
        logger.info(f"Updating content of file: {file_path}")
        
        # Write new content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(request.content)
        
        return {
            "success": True,
            "message": f"File content updated successfully"
        }
    
    except Exception as e:
        logger.error(f"Error updating file content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating file content: {str(e)}")

# Thêm endpoint cho download file
@router.get("/download-file/{path:path}", response_class=FileResponse)
async def download_file(
    path: str = Path(..., description="Path to the file to download, can include folder/subfolder"),
    current_user: dict = Depends(get_current_user)
):
    """
    Download a file from the data directory
    
    This endpoint allows administrators to download a file from the data directory.
    
    Args:
        path: Path to the file to download, can include folder/subfolder
        
    Returns:
        The file for download
    """
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can download training files")
    
    try:
        # Split path into folder and filename
        # If path has no slashes, assume it's a file in the root data directory
        if "/" not in path:
            file_path = os.path.join(DATA_DIR, path)
        else:
            # Split by last slash to get folder path and filename
            *folder_parts, filename = path.split("/")
            folder = "/".join(folder_parts)
            
            # Determine folder path
            if folder == "default" or not folder:
                folder_path = DATA_DIR
            else:
                # Xây dựng đường dẫn dựa trên các phần của folder
                current_path = DATA_DIR
                for part in folder_parts:
                    current_path = os.path.join(current_path, part)
                folder_path = current_path
                
            file_path = os.path.join(folder_path, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {path} not found")
        
        logger.info(f"Downloading file: {file_path}")
        
        # Return file for download
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path),
            media_type="application/octet-stream"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")
