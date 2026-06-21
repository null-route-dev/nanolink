import string
import random
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    original_url: HttpUrl

class LinkResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str

def generate_short_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

links_storage = {}

app = FastAPI(title="NanoLink")

@app.get("/")
async def root():
    return {"message": "NanoLink is running"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/links", response_model=LinkResponse, status_code=201)
async def create_link(link_data: LinkCreate):
    short_code = generate_short_code()
    while short_code in links_storage:
        short_code = generate_short_code()
    
    links_storage[short_code] = {
        "original_url": str(link_data.original_url),
        "created_at": datetime.now().isoformat()
    }
    
    return LinkResponse(
        short_code=short_code,
        original_url=str(link_data.original_url),
        created_at=links_storage[short_code]["created_at"]
    )

@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    link_data = links_storage.get(short_code)
    if not link_data:
        raise HTTPException(
            status_code=404,
            detail=f"Short code '{short_code}' not found"
        )
    
    return RedirectResponse(
        url=link_data["original_url"],
        status_code=307
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)