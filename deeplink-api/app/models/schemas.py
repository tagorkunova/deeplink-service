from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Any
import uuid


class DeepLinkCreate(BaseModel):
    targetUrl: str
    ttlSeconds: int = 3600
    payload: dict[str, Any] = {}

    @field_validator("targetUrl")
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("targetUrl must start with http:// or https://")
        return v

    @field_validator("ttlSeconds")
    @classmethod
    def validate_ttl(cls, v):
        if v <= 0:
            raise ValueError("ttlSeconds must be positive")
        if v > 86400 * 365:
            raise ValueError("ttlSeconds cannot exceed 1 year")
        return v


class DeepLinkResponse(BaseModel):
    id: uuid.UUID
    code: str
    targetUrl: str
    payload: dict[str, Any]
    createdAt: datetime
    expiresAt: datetime
    active: bool
    clickCount: int
    shortUrl: str

    model_config = {"from_attributes": True}


class DeepLinkListResponse(BaseModel):
    items: list[DeepLinkResponse]
    total: int
