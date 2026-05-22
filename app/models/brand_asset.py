from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.models import Base


class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(String(64), primary_key=True)
    merchant_id = Column(String(64), nullable=False)
    asset_type = Column(String(32), nullable=False, default="logo")  # logo, image, etc.
    file_path = Column(String(512), nullable=True)
    file_url = Column(String(512), nullable=True)
    original_name = Column(String(256), nullable=True)
    watermark_config = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
