from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models.models import Base
from core.config import settings

engine = create_async_engine(
    settings.database_url,
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
