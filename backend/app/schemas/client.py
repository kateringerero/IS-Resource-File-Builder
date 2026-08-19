from pydantic import BaseModel, HttpUrl
from typing import Any


class ClientCreateRequest(BaseModel):
    name: str
    platform_id: int
    website: str | None = None
    brand_tone: str | None = None
    notes: str | None = None
    selected_features_json: dict[str, Any]


class ClientUpdateRequest(BaseModel):
    name: str | None = None
    platform_id: int | None = None
    website: str | None = None
    brand_tone: str | None = None
    notes: str | None = None
    status: str | None = None
    selected_features_json: dict[str, Any] | None = None