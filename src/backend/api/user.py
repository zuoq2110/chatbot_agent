import logging
import hashlib
import secrets
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from bson import ObjectId
from ..db.mongodb import MongoDB, mongodb
from backend.models.user import UserCreate, UserResponse, UserLogin
from backend.models.responses import BaseResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Combine password and salt
    password_salt = f"{password}{salt}"
    
    # Hash using SHA-256
    password_hash = hashlib.sha256(password_salt.encode()).hexdigest()
    
    return password_hash, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify password against hash"""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == password_hash


@router.post("/", response_model=BaseResponse[UserResponse])
async def create_user(user: UserCreate):
    """Create a new user"""
    
    # Check if username exists
    existing_user = await mongodb.db.users.find_one({"username": user.username})
    
    if existing_user:
        # User already exists, raise HTTP exception
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập đã tồn tại"
        )
    
    # Hash password
    password_hash, salt = hash_password(user.password)
    
    # Create new user
    now = datetime.utcnow()
    new_user = {
        "username": user.username,
        "password_hash": password_hash,
        "salt": salt,
        "created_at": now,
        "updated_at": now
    }
    
    # Add optional fields if provided
    if user.student_code:
        # Check if student_code already exists
        existing_student = await mongodb.db.users.find_one({"student_code": user.student_code})
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã sinh viên đã tồn tại"
            )
        new_user["student_code"] = user.student_code
    
    if user.student_name:
        new_user["student_name"] = user.student_name
    
    if user.student_class:
        new_user["student_class"] = user.student_class
    
    try:
        # Insert into database
        result = await mongodb.db.users.insert_one(new_user)
        
        # Get created user
        created_user = await mongodb.db.users.find_one({"_id": result.inserted_id})
        
        # Prepare response (exclude sensitive fields)
        response_data = UserResponse(
            _id=str(created_user["_id"]),
            username=created_user["username"],
            student_code=created_user.get("student_code"),
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
    
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Có lỗi xảy ra khi tạo tài khoản"
        )


@router.get("/{username}", response_model=BaseResponse[dict])
async def get_user(username: str):
    """Get user by username"""
    
    # Find user by username
    user = await mongodb.db.users.find_one({"username": username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tên đăng nhập"
        )
    
    # Return user data including password_hash and salt for verification
    user_data = {
        "_id": str(user["_id"]),
        "username": user["username"],
        "student_code": user.get("student_code"),
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


@router.post("/users/login", response_model=BaseResponse[dict])
async def login_user(user_login: UserLogin):
    """Login user with username and password"""
    
    # Find user by username
    user = await mongodb.db.users.find_one({"username": user_login.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng"
        )
    
    # Verify password
    if not verify_password(user_login.password, user["password_hash"], user["salt"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng"
        )
    
    # Update last login time
    now = datetime.utcnow()
    await mongodb.db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"updated_at": now, "last_login": now}}
    )
    
    # Prepare response (same structure as get_user)
    user_data = {
        "_id": str(user["_id"]),
        "username": user["username"],
        "student_code": user.get("student_code"),
        "student_name": user.get("student_name"),
        "student_class": user.get("student_class"),
        "created_at": user["created_at"],
        "updated_at": now
    }
    
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Đăng nhập thành công",
        data=user_data
    )