from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Link
from core.database import get_db

async def get_link_repository(
    db: AsyncSession = Depends(get_db)
) -> "LinkRepository":
    return LinkRepository(db)

class LinkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_link(self, link: Link) -> Link:
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def get_link_by_short_code(self, short_code: str) -> Link | None:
        result = await self.db.execute(
            select(Link).where(Link.short_code == short_code)
        )
        return result.scalar_one_or_none()