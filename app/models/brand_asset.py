from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.models import Base


class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(String(64), primary_key=True)
    merchant_id = Column(String(64), nullable=False)
    logo_url = Column(String(512), nullable=True)
    watermark_config = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
