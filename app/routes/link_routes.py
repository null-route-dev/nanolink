from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse

from services.link_service import LinkService, get_link_service
from services.click_log_service import ClickLogService, get_click_log_service
from schemas.link_schemas import LinkCreate, LinkResponse

router = APIRouter()

@router.post("/links", response_model=LinkResponse, status_code=201)
async def create_link(
    link_data: LinkCreate,
    service: LinkService = Depends(get_link_service)
):
    return await service.create_short_link(link_data)

@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    like_service: LinkService = Depends(get_link_service),
    click_log_service: ClickLogService = Depends(get_click_log_service),
):
    ip = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("user-agent", "Unknown")
    original_url = await like_service.get_original_url(short_code)
    await click_log_service.create_click_log(short_code, ip, user_agent)
    return RedirectResponse(url=original_url, status_code=307)

@router.get("/{short_code}/stats")
async def get_link_stats(
    short_code: str,
    service: ClickLogService = Depends(get_click_log_service)
):
    return await service.get_log_stats(short_code)