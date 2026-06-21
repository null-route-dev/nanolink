import uvicorn
from fastapi import FastAPI

app = FastAPI(title="NanoLink")

@app.get("/")
def root():
    return {"message": "NanoLink is running"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)