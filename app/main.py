from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from app.api.v1 import production, merchant, wechat
from app.core.config import get_settings
from app.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="BIKON Marketing API",
    description="多模态自动化营销生产线后端服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")

app.include_router(production.router, prefix="/api/v1/production", tags=["Production"])
app.include_router(merchant.router, prefix="/api/v1/merchant", tags=["Merchant"])
app.include_router(wechat.router, prefix="/api/v1/wechat", tags=["WeChat"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bikon-api"}
