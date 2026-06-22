from fastapi import Depends
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Link, ClickLog
from core.database import get_db

async def get_click_log_repository(
    db: AsyncSession = Depends(get_db)
) -> "ClickLogRepository":
    return ClickLogRepository(db)

class ClickLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_click_log_by_short_code(self, short_code: str, ip_address: str, user_agent: str):
        stmt = insert(ClickLog).values(
            link_id=select(Link.id).where(Link.short_code == short_code).scalar_subquery(),
            clicked_at=func.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result
    
    async def get_click_log_stats_by_short_code(self, short_code: str):
        stmt = (
            select(
                Link.short_code,
                Link.original_url,
                Link.created_at,
                func.count(ClickLog.id).label("total_clicks")
            )
            .select_from(Link)
            .outerjoin(ClickLog, Link.id == ClickLog.link_id)
            .where(Link.short_code == short_code)
        )
        result = await self.db.execute(stmt)
        return result.mappings().first()