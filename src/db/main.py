from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Book, User
from sqlmodel import SQLModel
from src.config import Config
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    Config.ASYNC_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    )

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
async_session_factory = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session():
    async with async_session_factory() as session:
        yield session
