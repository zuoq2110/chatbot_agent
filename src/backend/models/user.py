from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    student_code: str
    student_name: Optional[str] = None
    student_class: Optional[str] = None


class UserResponse(BaseModel):
    _id: str
    student_code: str
    student_name: Optional[str] = None
    student_class: Optional[str] = None
    created_at: datetime
    updated_at: datetime 