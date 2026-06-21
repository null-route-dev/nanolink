from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

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

app = FastAPI(title="NanoLink", version="0.1.0", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "NanoLink is running"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)