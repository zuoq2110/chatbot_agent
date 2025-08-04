import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from bson import ObjectId
from backend.db.mongodb import mongodb
from backend.models.user import UserCreate, UserResponse, UserLogin
from backend.models.responses import BaseResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/users", response_model=BaseResponse[UserResponse])
async def create_user(user: UserCreate):
    """Create a new user or return existing user by student_code"""
    
    # Check if user already exists with this student_code
    existing_user = await mongodb.db.users.find_one({"student_code": user.student_code})
    
    if existing_user:
        # User already exists, return error for registration
        return BaseResponse(
            statusCode=status.HTTP_400_BAD_REQUEST,
            message="Mã sinh viên đã tồn tại",
            data=None
        )
    
    # Create new user
    now = datetime.utcnow()
    new_user = {
        "student_code": user.student_code,
        "created_at": now,
        "updated_at": now
    }
    
    # Add optional fields if provided
    if user.student_name:
        new_user["student_name"] = user.student_name
    
    if user.student_class:
        new_user["student_class"] = user.student_class
    
    # Add authentication fields if provided
    if user.password_hash:
        new_user["password_hash"] = user.password_hash
    
    if user.salt:
        new_user["salt"] = user.salt
    
    # Insert into database
    result = await mongodb.db.users.insert_one(new_user)
    
    # Get created user
    created_user = await mongodb.db.users.find_one({"_id": result.inserted_id})
    
    # Prepare response (exclude sensitive fields)
    response_data = UserResponse(
        _id=str(created_user["_id"]),
        student_code=created_user["student_code"],
        student_name=created_user.get("student_name"),
        student_class=created_user.get("student_class"),
        created_at=created_user["created_at"],
        updated_at=created_user["updated_at"]
    )
    
    return BaseResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Đăng ký thành công",
        data=response_data
    )


@router.get("/users/{student_code}", response_model=BaseResponse[dict])
async def get_user(student_code: str):
    """Get user by student_code (for login)"""
    
    user = await mongodb.db.users.find_one({"student_code": student_code})
    
    if not user:
        return BaseResponse(
            statusCode=status.HTTP_404_NOT_FOUND,
            message="Không tìm thấy mã sinh viên",
            data=None
        )
    
    # Return user data including password_hash and salt for verification
    user_data = {
        "_id": str(user["_id"]),
        "student_code": user["student_code"],
        "student_name": user.get("student_name"),
        "student_class": user.get("student_class"),
        "password_hash": user.get("password_hash"),
        "salt": user.get("salt"),
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }
    
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Lấy thông tin người dùng thành công",
        data=user_data
    ) 