from fastapi import APIRouter, HTTPException, status, Depends
from src.books.schemas import Book, BookCreateModel, BookUpdateModel
from typing import List
from src.db.main import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from uuid import UUID
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.db.models import Review
from src.reviews.service import ReviewService
    
book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])

    
@book_router.get("/", response_model=List[Book], dependencies=[Depends(role_checker)])
async def get_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books



@book_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_checker)])
async def create_book(book: BookCreateModel, session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)) -> Book: 
    user_uid = token_details.get("user").get("user_uid")
    new_book = await book_service.create_book(session, user_uid, book)
    return new_book


@book_router.post("/batch", status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_checker)])
async def create_book(books: List[BookCreateModel], session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)) -> List[Book]: 
    user_uid = token_details.get("user").get("user_uid")
    new_books = await book_service.create_books(session, user_uid, books)
    return new_books

@book_router.get("/{book_id}", dependencies=[Depends(role_checker)])
async def get_book(book_id: UUID, session: AsyncSession = Depends(get_session)) -> Book:
    book = await book_service.get_book_by_id(session, book_id)
    if book:
        return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.get("/{book_id}/reviews",  dependencies=[Depends(role_checker)])
async def get_book_reviews(book_id: UUID, session: AsyncSession = Depends(get_session)) -> List[Review]:
    reviews = await book_service.get_book_reviews(session=session, book_id=book_id)
    if reviews:
        return reviews
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book or Reviews not found")

@book_router.patch("/{book_id}", dependencies=[Depends(role_checker)])
async def update_book(book_id: UUID, updated_book: BookUpdateModel, session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)) -> Book:
    updated_book = await book_service.update_book_id(session, book_id, updated_book)
    if updated_book:
        return updated_book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_checker)])
async def delete_book(book_id: UUID, session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)):
    deleted_book = await book_service.delete_book(session, book_id)
    if delete_book != None:
            return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

