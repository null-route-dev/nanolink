from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.config import settings
from core.database import init_db, close_db
from routes.link_routes import link_router
from routes.click_log_routes import stats_router
from routes.user_routes import user_router

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

app.include_router(link_router)
app.include_router(stats_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)