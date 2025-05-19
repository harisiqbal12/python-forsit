from pydantic import BaseModel, EmailStr, field_validator, Field, model_validator
from typing import Optional
import re


class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8)

    @field_validator("username")
    @classmethod
    def username_validator(cls, v):
        if v is None:
            return v
        if not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username must contain only letters, numbers, and underscores"
            )
        if " " in v:
            raise ValueError("Username must not contains spaces")
        return v

    @field_validator("password")
    @classmethod
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

    @model_validator(mode="after")
    def at_least_one_identifier(self):
        if not (self.username or self.email):
            raise ValueError("Either username or email must be provided")
        return self
