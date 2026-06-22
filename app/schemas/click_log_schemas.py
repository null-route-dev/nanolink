from pydantic import BaseModel

class ClickLogStats(BaseModel):
    short_code: str
    original_url: str
    created_at: str
    total_clicks: int