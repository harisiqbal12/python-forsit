from sqlalchemy import Column, ForeignKey, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid


class Category(Base):
    __tablename__ = "category"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False)
    identifier = Column(String(50), nullable=False, unique=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("category.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children")
