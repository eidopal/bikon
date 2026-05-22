from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.models import Base
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True)
    merchant_id = Column(String(64), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    inputs = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
