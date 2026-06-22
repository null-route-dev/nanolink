from fastapi import HTTPException, Depends

from crud.click_log_crud import ClickLogRepository, get_click_log_repository
from schemas.click_log_schemas import ClickLogStats

async def get_click_log_service(
    repo: ClickLogRepository = Depends(get_click_log_repository)
) -> "ClickLogService":
    return ClickLogService(repo)

class ClickLogService:
    def __init__(self, repo: ClickLogRepository):
        self.repo = repo
    
    async def get_log_stats(self, short_code: str) -> ClickLogStats:
        stats = await self.repo.get_click_log_stats_by_short_code(short_code)

        if stats['short_code'] is None:
            raise HTTPException(status_code=404, detail="Link not found")
    
        return ClickLogStats(
            short_code=stats['short_code'],
            original_url=stats['original_url'],
            created_at=stats['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            total_clicks=stats['total_clicks']
        )

    async def create_click_log(
        self,
        short_code: str,
        ip: str,
        user_agent: str
    ) -> None:
        await self.repo.create_click_log_by_short_code(short_code, ip, user_agent)