from collections.abc import AsyncGenerator
import uuid
import datetime

from fastapi import Depends
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship

# IMPORT BOTH: SQLAlchemyBaseUserTableUUID (for the table) and SQLAlchemyUserDatabase (for the adapter)
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.generics import GUID


DATABASE_URL = "sqlite+aiosqlite:///./test.db" 

class Base(DeclarativeBase):
    pass

# FIX: Inherit from SQLAlchemyBaseUserTableUUID instead of SQLAlchemyUserDatabase
class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    # Points to "user.id" because SQLAlchemyBaseUserTableUUID creates a table named "user"
    user_id = Column(GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    user = relationship("User", back_populates="posts")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# This is required by app/users.py to wire up the UserManager dependency
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)