from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class SalesChannelBase(BaseModel):
    name: str
    status: Optional[str] = "ACTIVE"
    description: Optional[str] = None

class SalesChannelCreate(SalesChannelBase):
    pass

class SalesChannelUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class SalesChannel(SalesChannelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True