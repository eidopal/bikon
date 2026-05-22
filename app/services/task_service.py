import uuid
import json
from typing import Dict, Any, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task, TaskStatus


def generate_task_id() -> str:
    return f"task_{uuid.uuid4().hex[:10]}"


async def submit_task(db: AsyncSession, payload: dict) -> dict:
    task_id = generate_task_id()
    task = Task(
        id=task_id,
        merchant_id=payload.get("merchant_id", ""),
        status=TaskStatus.PENDING,
        inputs=json.dumps(payload.get("inputs", {})),
    )
    db.add(task)
    await db.commit()

    # 启动后台处理任务
    import asyncio
    asyncio.create_task(process_task(task_id, payload, db.bind))

    return {"task_id": task_id, "estimated_wait_ms": 8500}


async def process_task(task_id: str, payload: dict, engine):
    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(engine) as db:
        try:
            stmt = select(Task).where(Task.id == task_id)
            result = await db.execute(stmt)
            task = result.scalar_one_or_none()
            if not task:
                return

            task.status = TaskStatus.PROCESSING
            await db.commit()

            inputs = json.loads(task.inputs) if task.inputs else {}
            image_urls = inputs.get("images", [])

            from app.services.ai_service import generate_copywriting
            merchant_context = payload.get("industry_context", "")
            targets = payload.get("copywriting_targets", ["wechat_moments", "xiaohongshu"])
            copywriting = await generate_copywriting(image_urls, "", merchant_context, targets)

            processed_images = image_urls[:9] if image_urls else []

            result = {
                "task_status": "COMPLETED",
                "visual_assets": {"processed_images": processed_images},
                "copywriting": copywriting,
                "metadata": {
                    "processing_time_ms": 7200,
                    "audio_transcript": ""
                },
            }

            task.status = TaskStatus.COMPLETED
            task.result = json.dumps(result)
            await db.commit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            if task:
                task.status = TaskStatus.FAILED
                task.result = json.dumps({"error": str(e)})
                await db.commit()


async def get_task_result(db: AsyncSession, task_id: str) -> dict:
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        return {"task_status": "NOT_FOUND"}

    if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
        if task.result:
            try:
                return json.loads(task.result)
            except Exception:
                return {"task_status": task.status.value, "error": "Failed to parse result"}
        return {"task_status": task.status.value}

    return {"task_status": task.status.value}
