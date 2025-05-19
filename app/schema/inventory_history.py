from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class InventoryHistoryBase(BaseModel):
    inventory_id: UUID
    previous_quantity: int
    new_quantity: int
    change_reason: str
    changed_by: UUID

class InventoryHistoryCreate(InventoryHistoryBase):
    pass

class InventoryHistoryUpdate(BaseModel):
    previous_quantity: Optional[int] = None
    new_quantity: Optional[int] = None
    change_reason: Optional[str] = None
    changed_by: Optional[UUID] = None

class InventoryHistory(InventoryHistoryBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True