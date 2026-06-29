from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse

from services.link_service import LinkService, get_link_service
from services.click_log_service import ClickLogService, get_click_log_service
from schemas.link_schemas import LinkCreate, LinkUpdate, LinkResponse
from schemas.user_schemas import UserResponse
from core.security import get_current_user, get_current_user_optional

link_router = APIRouter(prefix="/links", tags=["links"])

@link_router.post("/", response_model=LinkResponse, status_code=201)
async def create_link(
    link_data: LinkCreate,
    service: LinkService = Depends(get_link_service),
    current_user_optional: UserResponse | None = Depends(get_current_user_optional)
):
    user_id = current_user_optional.id if current_user_optional else None
    return await service.create_short_link(link_data, user_id)

@link_router.get("/my", response_model=list[LinkResponse])
async def get_my_links(
    service: LinkService = Depends(get_link_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.get_user_links(current_user.id)

@link_router.put("/{short_code}", response_model=LinkResponse)
async def update_link(
    short_code: str,
    link_data: LinkUpdate,
    service: LinkService = Depends(get_link_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.update_link(short_code, str(link_data.original_url), current_user.id)

@link_router.delete("/{short_code}", status_code=204)
async def delete_link(
    short_code: str,
    service: LinkService = Depends(get_link_service),
    current_user: UserResponse = Depends(get_current_user)
):
    await service.delete_link(short_code, current_user.id)

@link_router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    like_service: LinkService = Depends(get_link_service),
    click_log_service: ClickLogService = Depends(get_click_log_service)
):
    ip = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("user-agent", "Unknown")
    original_url = await like_service.get_original_url(short_code)
    await click_log_service.create_click_log(short_code, ip, user_agent)
    return RedirectResponse(url=original_url, status_code=307)