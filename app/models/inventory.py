from sqlalchemy import Column, ForeignKey, String, Text, TIMESTAMP, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid


class Inventory(Base):
    __tablename__ = "investory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, default=0)
    last_restock_date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    product = relationship("Product", back_populates="inventory", uselist=False)
    history = relationship("InventoryHistory", back_populates="inventory")

