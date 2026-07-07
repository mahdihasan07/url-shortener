from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class URLCreate(BaseModel):
    original_url: HttpUrl


class URLOut(BaseModel):
    id: int
    short_code: str
    original_url: str
    short_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClickOut(BaseModel):
    clicked_at: datetime
    referrer: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True


class StatsOut(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    recent_clicks: list[ClickOut]