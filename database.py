from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
DATABASE_URL="sqlite+aiosqlite:///./todos.db"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    await engine.dispose()

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession,
    autocommit=False, 
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

class Link(Base):
    __tablename__ = 'links'
    
    id = Column(Integer, primary_key=True)
    short_code = Column(String(20), nullable=False, unique=True)
    original_url = Column(Text(), nullable=False)
    created_at = Column(DateTime, default=datetime.now)