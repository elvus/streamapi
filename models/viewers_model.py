from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from models.objectid import PydanticObjectId

class Viewer(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias='_id')
    uuid: Optional[str] = Field(default_factory=lambda: str(uuid4()), alias='uuid')
    name: str
    color: Optional[str] = "#1890ff"
    pin: Optional[str] = None
    status: Optional[str] = None
    use_pin: Optional[bool] = False
    user_uuid: str
    created_at: Optional[datetime] = Field(datetime.now(), alias='createdAt')
    updated_at: Optional[datetime] = Field(None, alias='updatedAt')

    def to_json(self):
        data = self.model_dump()
        return data
    
    def to_bson(self):
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        if data.get("pin") is None:
            data.pop("pin", None)
        if data.get("use_pin") is None:
            data.pop("use_pin", None)
        return data
        