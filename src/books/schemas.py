from datetime import date

from pydantic import BaseModel
from uuid import UUID

from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel

class Book(BaseModel):
    uid: UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    reviews: list[ReviewModel]
    tags: list[TagModel]
    
class BookUpdateModel(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    page_count: int | None = None
    language: str | None = None
    
class BookCreateModel(BaseModel):
    title: str 
    author: str 
    publisher: str 
    published_date: date
    page_count: int 
    language: str 
    
    
class BookSimpleRead(BaseModel):
    title: str 
    author: str 
