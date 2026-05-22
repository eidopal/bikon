from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.api.v1 import production, merchant, wechat
from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_logger
from app.database import init_db
from app.core.queue import setup_redis, close_redis, WorkerSettings
from app.services.task_service import process_task
from app.utils.response import (
    success_response,
    validation_exception_handler,
    http_exception_handler,
    global_exception_handler,
)

setup_logging()
logger = get_logger(__name__)

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

# 全局异常处理器
@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    return await validation_exception_handler(request, exc)

@app.exception_handler(StarletteHTTPException)
async def http_handler(request, exc):
    return await http_exception_handler(request, exc)

@app.exception_handler(Exception)
async def global_handler(request, exc):
    return await global_exception_handler(request, exc)

WorkerSettings.functions = [process_task]


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")

    try:
        await setup_redis()
        logger.info("Redis queue connected.")
    except Exception as e:
        logger.warning(f"Redis unavailable, using asyncio fallback: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()
    logger.info("Redis queue disconnected.")

app.include_router(production.router, prefix="/api/v1/production", tags=["Production"])
app.include_router(merchant.router, prefix="/api/v1/merchant", tags=["Merchant"])
app.include_router(wechat.router, prefix="/api/v1/wechat", tags=["WeChat"])

@app.get("/health")
async def health_check():
    return success_response(data={"service": "bikon-api"})
