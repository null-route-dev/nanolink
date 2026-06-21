import string
import random
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select

from database import init_db, close_db, Link, AsyncSessionLocal

class LinkCreate(BaseModel):
    original_url: HttpUrl

class LinkResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str

def generate_short_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        raise
    
    yield
    
    await close_db()

app = FastAPI(title="NanoLink", version="0.1.0", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "NanoLink is running"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/links", response_model=LinkResponse, status_code=201)
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

@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Link).where(Link.short_code == short_code)
        )
        link = result.scalar_one_or_none()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return RedirectResponse(url=link.original_url, status_code=307)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)