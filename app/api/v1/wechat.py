from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.wechat_service import code2session, msg_sec_check, img_sec_check
from app.utils.response import success_response

router = APIRouter()


class Code2SessionRequest(BaseModel):
    code: str


@router.post("/code2session")
async def wechat_login(
    payload: Code2SessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """微信小程序登录"""
    result = await code2session(payload.code)

    errocde = result.get("errcode")
    if errocde and errocde != 0:
        raise HTTPException(
            status_code=400,
            detail=f"微信登录失败: {result.get('errmsg', '未知错误')}"
        )

    openid = result.get("openid")
    if not openid:
        raise HTTPException(status_code=400, detail="微信登录失败: 未获取到 openid")

    from app.models.user import User
    from app.core.auth import create_access_token
    from sqlalchemy import select
    import uuid

    stmt = select(User).where(User.openid == openid)
    query_result = await db.execute(stmt)
    user = query_result.scalar_one_or_none()

    if user is None:
        user = User(
            id=f"user_{uuid.uuid4().hex[:10]}",
            openid=openid,
            unionid=result.get("unionid"),
        )
        db.add(user)

    user.last_login_at = func.now()
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, user.openid)

    return success_response(
        data={
            "token": token,
            "user_id": user.id,
            "openid": user.openid,
            "unionid": result.get("unionid"),
            "merchant_id": user.merchant_id,
        },
        msg="Success",
    )


class TextSecCheckRequest(BaseModel):
    content: str


@router.post("/msg-sec-check")
async def wechat_msg_sec_check(payload: TextSecCheckRequest):
    """微信文本安全审查"""
    result = await msg_sec_check(payload.content)
    return success_response(data=result, msg="Success")


class ImageSecCheckRequest(BaseModel):
    image_url: str


@router.post("/img-sec-check")
async def wechat_img_sec_check(payload: ImageSecCheckRequest):
    """微信图片安全审查"""
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.get(payload.image_url)
        resp.raise_for_status()
        result = await img_sec_check(resp.content)

    return success_response(data=result, msg="Success")
