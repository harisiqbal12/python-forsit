from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app.schema.inventory_history import InventoryHistory
from app.schema.product import ProductSecondary


class InventoryBase(BaseModel):
    product_id: UUID
    quantity: int = 0
    last_restock_date: Optional[datetime] = None


class InventoryCreate(InventoryBase):
    change_reason: str
    pass


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    last_restock_date: Optional[datetime] = None
    change_reason: str


class Inventory(InventoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryDetails(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    last_restock_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    product: ProductSecondary
    history: List[InventoryHistory]

    class Config:
        from_attributes = True
