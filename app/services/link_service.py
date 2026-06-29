import string
import random

from fastapi import HTTPException, Depends

from crud.link_crud import LinkRepository, get_link_repository
from models.models import Link
from schemas.link_schemas import LinkCreate, LinkResponse
from core.cache import cache_service

async def get_link_service(
    repo: LinkRepository = Depends(get_link_repository)
) -> "LinkService":
    return LinkService(repo)

class LinkService:
    def __init__(self, repo: LinkRepository):
        self.repo = repo

    async def create_short_link(self, link_data: LinkCreate, user_id: int | None) -> LinkResponse:
        while True:
            short_code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6))
            existing = await self.repo.get_link_by_short_code(short_code)
            if not existing:
                break

        new_link = await self.repo.create_link(
            Link(
                short_code=short_code,
                original_url=str(link_data.original_url),
                user_id=user_id
            )
        )

        return LinkResponse(
            short_code=new_link.short_code,
            original_url=new_link.original_url,
            created_at=new_link.created_at.isoformat(),
            owner_id=user_id
        )

    async def get_user_links(self, user_id: int) -> list[LinkResponse]:
        links = await self.repo.get_links_by_user_id(user_id)
        return [
            LinkResponse(
                short_code=link.short_code,
                original_url=link.original_url,
                created_at=link.created_at.isoformat(),
                owner_id=link.user_id
            )
            for link in links
        ]
    
    async def update_link(self, short_code: str, new_url: str, user_id: int) -> LinkResponse:
        updated = await self.repo.update_link_url(short_code, new_url, user_id)
        if updated is None:
            raise HTTPException(status_code=404, detail="Link not found or not owned by user")
        
        await cache_service.delete(f"link:original:{short_code}")

        return LinkResponse(
            short_code=updated.short_code,
            original_url=updated.original_url,
            created_at=updated.created_at.isoformat(),
            owner_id=updated.user_id
        )

    async def delete_link(self, short_code: str, user_id: int) -> None:
        deleted = await self.repo.delete_link(short_code, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Link not found or not owned by user")
        
        await cache_service.delete(f"link:original:{short_code}")

    async def get_original_url(self, short_code: str) -> str:
        cache_key = f"link:original:{short_code}"
        cached_url = await cache_service.get(cache_key)

        if cached_url:
            return cached_url

        link = await self.repo.get_link_by_short_code(short_code)
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        await cache_service.set(cache_key, link.original_url)
        
        return link.original_url