from fastapi import APIRouter, Depends

from services.click_log_service import ClickLogService, get_click_log_service

stats_router = APIRouter(prefix="/stats", tags=["stats"])

@stats_router.get("/{short_code}")
async def get_link_stats(
    short_code: str,
    service: ClickLogService = Depends(get_click_log_service)
):
    return await service.get_log_stats(short_code)