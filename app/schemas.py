
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class URLCreate(BaseModel):

    original_url: HttpUrl

    custom_alias: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )

    expires_at: datetime | None = None


class URLResponse(BaseModel):

    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: datetime | None

