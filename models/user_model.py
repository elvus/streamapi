from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from models.objectid import PydanticObjectId

class Address(BaseModel):
    street: str
    city: str
    country: str

class Profile(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    address: Optional[Address] = None

class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias='_id')
    username: str
    password: str
    email: str
    privileges: list
    role: Optional[str] = None
    profile: Optional[Profile] = None
    created_at: Optional[datetime] = Field(None, alias='createdAt')
    updated_at: Optional[datetime] = Field(None, alias='updatedAt')

    def to_json(self):
        return self.model_dump()
    
    def to_bson(self):
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data