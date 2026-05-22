from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.wechat_service import code2session, msg_sec_check, img_sec_check
from app.utils.response import success_response

router = APIRouter()


class Code2SessionRequest(BaseModel):
    code: str


@router.post("/code2session")
async def wechat_login(payload: Code2SessionRequest):
    """微信小程序登录"""
    result = await code2session(payload.code)

    if result.get("errcode"):
        raise HTTPException(
            status_code=400,
            detail=f"微信登录失败: {result.get('errmsg', '未知错误')}"
        )

    return success_response(
        data={
            "openid": result.get("openid"),
            "session_key": result.get("session_key"),
            "unionid": result.get("unionid"),
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
