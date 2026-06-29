from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    original_url: HttpUrl

class LinkUpdate(BaseModel):
    original_url: HttpUrl

class LinkResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str
    owner_id: int | None