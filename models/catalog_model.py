from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from models.objectid import PydanticObjectId
from datetime import datetime, timezone

class Episodes(BaseModel):
    episode_number: int
    title: Optional[str] = None
    intro_start_time: Optional[str] = None
    intro_end_time: Optional[str] = None
    next_episode_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    file_path: Optional[str] = None
    status: Optional[str] = None

class Seasons(BaseModel):
    season_number: int
    episodes: List[Episodes]


class StreamContent(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias='_id')
    uuid: Optional[str] = Field(default_factory=lambda: str(uuid4()), alias='uuid')
    title: str
    type: str
    release_year: int
    genre: List[str]
    rating: float
    description: Optional[str] = None
    cast: Optional[List[str]] = None
    seasons: Optional[List[Seasons]] = None
    duration_seconds: Optional[float] = None
    intro_start_time: Optional[str] = None
    intro_end_time: Optional[str] = None
    file_path: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_json(self):
        data = self.model_dump()
        return data
    
    def to_bson(self):
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        if data.get("seasons") is None:
            data.pop("seasons", None)
        if data.get("created_at") is None:
            data["created_at"] = datetime.now(timezone.utc)
        if data.get("updated_at") is None:
            data["updated_at"] = datetime.now(timezone.utc)
        if data.get("intro_start_time") is None:
            data.pop("intro_start_time", None)
        if data.get("intro_end_time") is None:
            data.pop("intro_end_time", None)
        return data