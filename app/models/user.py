from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    openid = Column(String(128), unique=True, nullable=False, index=True)
    unionid = Column(String(128), nullable=True)
    nickname = Column(String(128), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    merchant_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
