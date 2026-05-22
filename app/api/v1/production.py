from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.task_service import submit_task, get_task_result
from app.utils.response import success_response

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
    return success_response(data=result, msg="Task accepted")


@router.get("/task-result/{task_id}")
async def get_task_result_endpoint(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await get_task_result(db, task_id)
    if result.get("task_status") == "NOT_FOUND":
        return success_response(data=None, msg="Task not found", code=404)
    return success_response(data=result, msg="Success")
