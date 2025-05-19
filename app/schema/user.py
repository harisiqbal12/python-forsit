from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserBase(BaseModel):
    email: EmailStr
    username: str
    name: str
    avatar: Optional[str] = None
    status: str = "ACTIVE"

    @field_validator("username")
    def username_validator(cls, v):
        if not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username must contain only letters, numbers, and underscores"
            )
        if " " in v:
            raise ValueError("Username must not contains spaces")
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    def password_validator(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True