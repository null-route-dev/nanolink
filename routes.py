import string
import random

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from sqlalchemy import select

from database import AsyncSessionLocal
from models import Link
from schemas import LinkCreate, LinkResponse

router = APIRouter()

def generate_short_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@router.post("/links", response_model=LinkResponse, status_code=201)
async def create_link(link_data: LinkCreate):
    async with AsyncSessionLocal() as session:
        while True:
            short_code = generate_short_code()
            existing = await session.execute(
                select(Link).where(Link.short_code == short_code)
            )
            if not existing.scalar_one_or_none():
                break
        
        new_link = Link(
            short_code=short_code,
            original_url=str(link_data.original_url)
        )
        session.add(new_link)
        await session.commit()
        await session.refresh(new_link)
        
        return LinkResponse(
            short_code=new_link.short_code,
            original_url=new_link.original_url,
            created_at=new_link.created_at.isoformat()
        )

@router.get("/{short_code}")
async def redirect_to_url(short_code: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Link).where(Link.short_code == short_code)
        )
        link = result.scalar_one_or_none()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return RedirectResponse(url=link.original_url, status_code=307)