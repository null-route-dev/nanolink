from fastapi import Depends
from sqlalchemy import select, update, delete
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
    
    async def get_links_by_user_id(self, user_id: int) -> list[Link]:
        result = await self.db.execute(
            select(Link).where(Link.user_id == user_id)
        )
        return result.scalars().all()

    async def update_link_url(self, short_code: str, new_url: str, user_id: int) -> Link | None:
        result = await self.db.execute(
            update(Link)
            .where(Link.short_code == short_code, Link.user_id == user_id)
            .values(original_url=new_url)
            .returning(Link)
        )
        updated = result.scalar_one_or_none()
        await self.db.commit()
        if updated:
            await self.db.refresh(updated)
        return updated

    async def delete_link(self, short_code: str, user_id: int) -> bool:
        result = await self.db.execute(
            delete(Link)
            .where(Link.short_code == short_code, Link.user_id == user_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_link_by_short_code(self, short_code: str) -> Link | None:
        result = await self.db.execute(
            select(Link).where(Link.short_code == short_code)
        )
        return result.scalar_one_or_none()