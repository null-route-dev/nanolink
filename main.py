from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import settings
from database import init_db, close_db
from routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        raise
    
    yield
    
    await close_db()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "NanoLink is running"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)