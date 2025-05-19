import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base

class SalesSnapshot(Base):
    __tablename__ = "sales_snapshot"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    total_sales = Column(Integer, nullable=False)
    total_revenue = Column(Numeric(14, 4), nullable=False)
    average_sales = Column(Numeric(14, 4), nullable=False)
    average_revenue = Column(Numeric(14, 4), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    total_products = Column(Integer, nullable=False)
    total_tax = Column(Numeric(14, 4), nullable=False)
    total_shipping = Column(Numeric(14, 4), nullable=False)
    total_discount = Column(Numeric(14, 4), nullable=False)
    interval = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())