from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from services import LinkService, get_link_service
from schemas import LinkCreate, LinkResponse

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
    service: LinkService = Depends(get_link_service)
):
    original_url = await service.get_original_url(short_code)
    return RedirectResponse(url=original_url, status_code=307)