from datetime import datetime, date
from typing import List, Optional
import sqlalchemy.dialects.postgresql as pg
import uuid
from sqlmodel import Column, Field, Relationship, SQLModel, func


class User(SQLModel, table=True):
    __tablename__ = 'user_accounts'
    
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description": "Unique identifier for the user account"}
        )
    )
    username: str
    first_name: str = Field(nullable=True)
    last_name: str = Field(nullable=True)
    role: str = Field(
        sa_column=Column(
            pg.VARCHAR,
            nullable=False,
            server_default="user"
        )
    )
    is_verified: bool = False
    email: str
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=func.now()))
    
    books: List["Book"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: List["Review"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    
    def __repr__(self) -> str:
        return f"<User {self.username})>"

    
class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(
            sa_column=Column(
                pg.UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                unique=True,
                nullable=False
            )
        )
    rating: int = Field(le=5)
    review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()))
    
    user_uid: uuid.UUID | None = Field(default=None, foreign_key="user_accounts.uid")
    user: Optional["User"] = Relationship(back_populates="reviews")
    
    book_id: uuid.UUID | None = Field(default=None, foreign_key="books.uid")
    book: Optional["Book"] = Relationship(back_populates="reviews")
    
    def __repr__(self):
        return f"<Review for book {self.book_id} by user {self.user_uid}>"
    

class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)
    
class Book(SQLModel, table=True):
    __tablename__ = "books"
    
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            unique=True,
            nullable=False
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()))
    user_uid: uuid.UUID | None = Field(default=None, foreign_key="user_accounts.uid")
    
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})
    tags: List["Tag"] = Relationship(back_populates="books", link_model=BookTag, sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"book {self.title}"


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now()))

    books: List[Book] = Relationship(back_populates="tags", link_model=BookTag, sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"

