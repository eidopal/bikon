from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.merchant import Merchant
from app.models.task import Task, TaskStatus
from app.models.brand_asset import BrandAsset
from app.models.user import User
