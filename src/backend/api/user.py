import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from bson import ObjectId
from backend.db.mongodb import mongodb
from backend.models.user import UserCreate, UserResponse
from backend.models.responses import BaseResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/users", response_model=BaseResponse[UserResponse])
async def create_user(user: UserCreate):
    """Create a new user or return existing user by student_code"""
    
    # Check if user already exists with this student_code
    existing_user = await mongodb.db.user.find_one({"student_code": user.student_code})
    
    if existing_user:
        # User already exists, return it
        response_data = UserResponse(
            _id=str(existing_user["_id"]),
            student_code=existing_user["student_code"],
            student_name=existing_user.get("student_name"),
            student_class=existing_user.get("student_class"),
            created_at=existing_user["created_at"],
            updated_at=existing_user["updated_at"]
        )

        return BaseResponse(
            statusCode=status.HTTP_200_OK,
            message="User already exists",
            data=response_data
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
    
    # Insert into database
    result = await mongodb.db.users.insert_one(new_user)
    
    # Get created user
    created_user = await mongodb.db.users.find_one({"_id": result.inserted_id})
    
    # Prepare response
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
        message="User created successfully",
        data=response_data
    ) 