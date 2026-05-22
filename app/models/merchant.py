import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.models import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String(64), primary_key=True, default=lambda: f"mer_{uuid.uuid4().hex[:10]}")
    name = Column(String(128), nullable=False)
    industry_context = Column(Text, nullable=True)
    brand_symbol = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
