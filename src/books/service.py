from typing import List

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.books.schemas import BookCreateModel,BookUpdateModel
from datetime import datetime

from src.db.models import Book, Review

class BookService:
    
    async def get_all_books(self, session: AsyncSession) -> list:
        """_summary_
        Get a list of all books
        
        Returns:
            list: list of books
        """
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all() 
    
    async def get_books_by_user(self, user_uid: str, session: AsyncSession) -> list:
        """_summary_
        Get a list of all books from user
        
        Returns:
            list: list of books
        """
        statement = (
                select(Book)
                .where(Book.user_uid == user_uid)
                .order_by(desc(Book.created_at))
                )
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def create_book(self, session: AsyncSession, user_uid: str, book_data: BookCreateModel) -> Book:
        """_summary_
        Create a new book
        
        Args:
            book_data (dict): book data
            user_uid: user uid from jwt
        Returns:
            Book: created book
        """
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.user_uid = user_uid
        session.add(new_book)
        await session.commit()
        return new_book 
    
    async def create_books(self, session, user_uid, books: list[BookCreateModel]) -> list[Book]:
        new_books = [
            Book(**book.model_dump(), user_uid=user_uid)
            for book in books
        ]
        session.add_all(new_books)
        await session.commit()
        return new_books
    
    async def get_book_by_id(self, session: AsyncSession, book_id: str) -> Book:
        """_summary_
        Get a book by id
        
        Args:
            book_id (str): book id
            
        Returns:
            Book: book
        """
        statement = select(Book).where(Book.uid == book_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_book_reviews(self, session: AsyncSession, book_id: str) -> List[Review]:
            """_summary_
            Get a book by id
            
            Args:
                book_id (str): book id
                
            Returns:
                Book: book
            """
            book = await self.get_book_by_id(session, book_id)
            if book:
                return book.reviews
            return None
    
    async def update_book_id(self, session: AsyncSession, book_id: str, update_book: BookUpdateModel):
        """_summary_
        Update a book by id
        Args:
            book_id (str): book id
            update_book (BookUpdateModel): 
        Returns:
        Book: the updated book
        """
        
        book_to_update = await self.get_book_by_id(session, book_id)
        if book_to_update:
            for k, v in update_book.model_dump(exclude_unset=True).items():
                setattr(book_to_update, k, v)
            await session.commit()
            return book_to_update
        else:
            return None
        
    async def delete_book(self, session: AsyncSession, book_id: str):
        """_summary_
        Delete a book by id
        Args:
            book_id (str): book id
        Returns:
        Book: the deleted book
        """
        
        book_to_delete = await self.get_book_by_id(session, book_id)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return book_to_delete
        else:
            return None
    