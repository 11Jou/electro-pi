from pydantic import BaseModel, field_validator
from datetime import datetime
import re


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(self, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return password

    @field_validator("email")
    @classmethod
    def validate_email(self, email: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            raise ValueError("Invalid email address")
        return email




class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: datetime
    updated_at: datetime