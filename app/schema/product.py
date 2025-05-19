from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from app.schema.user import User
from app.schema.category import Category
from typing import Optional


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    price: float
    cost_price: float
    avatar: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    category_id: Optional[UUID] = None


class ProductCreate(ProductBase):
    category_identifier: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    avatar: Optional[str] = None
    status: Optional[str] = None
    category_identifier: Optional[str] = None


class Product(ProductBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    creator: Optional[User] = None
    category: Optional[Category] = None

    class Config:
        from_attributes = True


class ProductSecondary(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    sku: str
    price: float
    cost_price: float
    avatar: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
