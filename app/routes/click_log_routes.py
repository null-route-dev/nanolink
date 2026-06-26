from fastapi import APIRouter, Depends

from services.click_log_service import ClickLogService, get_click_log_service
from schemas.user_schemas import UserResponse
from core.security import get_current_user

stats_router = APIRouter(prefix="/stats", tags=["stats"])

@stats_router.get("/{short_code}")
async def get_link_stats(
    short_code: str,
    service: ClickLogService = Depends(get_click_log_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.get_log_stats(short_code, current_user.id)