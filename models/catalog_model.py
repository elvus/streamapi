from typing import List, Optional
from pydantic import BaseModel, Field

from models.objectid import PydanticObjectId
from datetime import datetime, timezone

class Episodes(BaseModel):
    episode_number: int
    title: str
    duration_seconds: int
    file_path: str

class Seasons(BaseModel):
    season_number: int
    episodes: List[Episodes]


class StreamContent(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias='_id')
    title: str
    type: str
    release_year: int
    genre: List[str]
    rating: float
    description: Optional[str] = None
    cast: Optional[List[str]] = None
    seasons: Optional[List[Seasons]] = None
    duration_seconds: Optional[int] = None
    file_path: Optional[str] = None
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc), alias='createdAt')
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc), alias='updatedAt')

    def to_json(self):
        return self.model_dump()
    
    def to_bson(self):
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        if data.get("seasons") is None:
            data.pop("seasons", None)
        return data        