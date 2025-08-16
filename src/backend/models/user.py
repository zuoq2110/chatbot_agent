from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str  # Raw password (sẽ được hash)
    student_code: Optional[str] = None
    student_name: Optional[str] = None
    student_class: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    _id: str
    username: str
    student_code: Optional[str] = None
    student_name: Optional[str] = None
    student_class: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Không trả về password_hash và salt trong response 