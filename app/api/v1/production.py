from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pathlib import Path
from app.database import get_db
from app.models.user import User
from app.core.auth import get_current_user
from app.core.config import get_settings
from app.services.task_service import submit_task, get_task_result
from app.utils.response import success_response

router = APIRouter()
settings = get_settings()


@router.get("/ping")
async def ping():
    return {"pong": True}


@router.post("/submit-task")
async def submit_task_endpoint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await submit_task(db, payload)
    return success_response(data=result, msg="Task accepted")


@router.post("/submit-with-files")
async def submit_with_files_endpoint(
    files: List[UploadFile] = File(...),
    merchant_id: str = Form(""),
    industry_context: str = Form(""),
    copywriting_targets: str = Form("wechat_moments,xiaohongshu"),
    watermark_text: str = Form("BIKON"),
    audio_url: str = Form(""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """小程序端提交：直接上传图片文件"""
    from app.utils.storage import save_upload

    image_urls = []
    for file in files:
        file_info = await save_upload(file, subfolder="task-images")
        image_urls.append(file_info["url"])

    targets = [t.strip() for t in copywriting_targets.split(",") if t.strip()]

    payload = {
        "merchant_id": merchant_id or (current_user.merchant_id or ""),
        "industry_context": industry_context,
        "inputs": {
            "images": image_urls,
            "audio_url": audio_url,
        },
        "copywriting_targets": targets,
        "watermark_text": watermark_text,
    }

    result = await submit_task(db, payload)
    result["uploaded_images"] = image_urls
    return success_response(data=result, msg="Task accepted with uploaded files")


@router.get("/task-result/{task_id}")
async def get_task_result_endpoint(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await get_task_result(db, task_id)
    if result.get("task_status") == "NOT_FOUND":
        return success_response(data=None, msg="Task not found", code=404)
    return success_response(data=result, msg="Success")


@router.get("/tasks")
async def list_tasks_endpoint(
    merchant_id: str = "",
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询任务列表，按创建时间倒序"""
    from sqlalchemy import select, func as sql_func
    from app.models.task import Task

    mid = merchant_id or current_user.merchant_id or ""

    stmt = (
        select(Task)
        .where(Task.merchant_id == mid)
        .order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    count_stmt = (
        select(sql_func.count(Task.id)).where(Task.merchant_id == mid)
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    return success_response(
        data={
            "tasks": [
                {
                    "task_id": t.id,
                    "status": t.status.value,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                }
                for t in tasks
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        msg="Success",
    )
