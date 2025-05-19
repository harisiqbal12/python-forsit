from sqlalchemy import Column, Text, TIMESTAMP, String, ForeignKey, func, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base_class import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(100), unique=True, nullable=False)
    channel_id = Column(
        UUID(as_uuid=True), ForeignKey("sales_channel.id"), nullable=False
    )
    order_date = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    total_amount = Column(DECIMAL(12, 4), nullable=False)
    tax_amount = Column(DECIMAL(10, 4), nullable=False)
    shipping_amount = Column(DECIMAL(10, 4), nullable=False)
    discount_amount = Column(DECIMAL(10, 4), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    shipping_address = Column(Text)
    billing_address = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    channel = relationship("SalesChannel", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", uselist=True)
