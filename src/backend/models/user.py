from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    student_code: str
    student_name: Optional[str] = None
    student_class: Optional[str] = None
    password_hash: Optional[str] = None  # Hash của mật khẩu
    salt: Optional[str] = None           # Salt để hash mật khẩu


class UserLogin(BaseModel):
    student_code: str
    password: str


class UserResponse(BaseModel):
    _id: str
    student_code: str
    student_name: Optional[str] = None
    student_class: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Không trả về password_hash và salt trong response 