from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderItemSecondary(BaseModel):
    product_id: UUID
    quantity: int


class OrderItemCreate(OrderItemSecondary):
    pass


class OrderItemUpdate(BaseModel):
    product_id: Optional[UUID] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None

class OrderItem(OrderItemBase):
    id: UUID
    order_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    order_number: str
    channel_id: UUID
    order_date: Optional[datetime] = None
    total_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    status: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None

class OrderBaseSecondary(BaseModel):
    channel_id: UUID
    order_date: Optional[datetime] = None
    status: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None


class OrderCreate(OrderBaseSecondary):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    order_number: Optional[str] = None
    channel_id: Optional[UUID] = None
    order_date: Optional[datetime] = None
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    shipping_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None

class Order(OrderBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem]

    class Config:
        from_attributes = True
