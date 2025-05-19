from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    status: Optional[str] = "ACTIVE"
    identifier: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    identifier: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class Category(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True


class CategoryDetail(CategoryBase):
    id: UUID
    parent: Optional[Category] = None

    class Config:
        from_attributes = True
