from contextlib import asynccontextmanager
from src.db.main import init_db
from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.middleware import register_middlewares
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from src.errors import register_error_handlers

version = "v1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    

app = FastAPI(
    title="Bookly",
    description="A RESTful API for a book review web service",
    version=version,
    # lifespan=lifespan
    
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Ssali Jonathan",
        "url": "https://github.com/jod35",
        "email": "ssalijonathank@gmail.com",
    },
    terms_of_service="httpS://example.com/tos",

)

register_error_handlers(app)
register_middlewares(app)

app.include_router(
    book_router,
    prefix=f"/api/{version}/books",
    tags=["Books"]
)

app.include_router(
    auth_router,
    prefix=f"/api/{version}/auth",
    tags=["Auth"],
)

app.include_router(
    review_router,
    prefix=f"/api/{version}/reviews",
    tags=["Auth"],
)

app.include_router(
    tags_router,
    prefix=f"/api/{version}/tags",
    tags=["Tags"],
)



