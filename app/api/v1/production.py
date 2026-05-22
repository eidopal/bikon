from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.task_service import submit_task, get_task_result

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"pong": True}


@router.post("/submit-task")
async def submit_task_endpoint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    result = await submit_task(db, payload)
    return {"code": 200, "msg": "Task accepted", "data": result}


@router.get("/task-result/{task_id}")
async def get_task_result_endpoint(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await get_task_result(db, task_id)
    if result.get("task_status") == "NOT_FOUND":
        return {"code": 404, "msg": "Task not found", "data": None}
    return {"code": 200, "msg": "Success", "data": result}
