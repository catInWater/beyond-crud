from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from src.books.schemas import Book
from src.reviews.schemas import ReviewModel

class UserLoginModel(BaseModel):
    email: str
    password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "123456@qq.com",
                "password": "123456"
            }
        }
    }

    
class UserRegisterModel(BaseModel):
    username: str = Field(max_length=20)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    first_name: str | None = Field(default=None, max_length=20)
    last_name: str | None = Field(default=None, max_length=20)

class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: UUID
    username: str
    email: str 
    first_name: str | None
    last_name: str | None
    role: str
    is_verified: bool 
    created_at: datetime
    
class UserBook(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]
    
class EmailModel(BaseModel):
    addresses: List[str]
    
class PasswordResetRequestModel(BaseModel):
    email: str
    
class UserPassword(UserModel):
    password_hash: str
    
class PasswordModel(BaseModel):
    password: str
