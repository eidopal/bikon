import httpx
import time
import json
from app.core.config import get_settings

settings = get_settings()

# 内存缓存 access_token
_access_token_cache = {"token": None, "expires_at": 0}


async def get_access_token() -> str:
    """获取微信 access_token，带缓存"""
    now = time.time()
    if _access_token_cache["token"] and _access_token_cache["expires_at"] > now + 300:
        return _access_token_cache["token"]

    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if "access_token" not in data:
        raise Exception(f"Failed to get access_token: {data}")

    _access_token_cache["token"] = data["access_token"]
    _access_token_cache["expires_at"] = now + data.get("expires_in", 7200)
    return data["access_token"]


async def code2session(code: str) -> dict:
    """微信小程序登录 code2Session"""
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        return resp.json()


async def msg_sec_check(content: str) -> dict:
    """微信内容安全审查（文本）"""
    try:
        access_token = await get_access_token()
        url = f"https://api.weixin.qq.com/wxa/msg_sec_check?access_token={access_token}"
        payload = {"content": content}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            return resp.json()
    except Exception as e:
        print(f"msg_sec_check failed: {e}")
        return {"errcode": -1, "errmsg": str(e)}


async def img_sec_check(image_data: bytes) -> dict:
    """微信内容安全审查（图片）"""
    try:
        access_token = await get_access_token()
        url = f"https://api.weixin.qq.com/wxa/img_sec_check?access_token={access_token}"
        files = {"media": ("image.jpg", image_data, "image/jpeg")}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, files=files)
            return resp.json()
    except Exception as e:
        print(f"img_sec_check failed: {e}")
        return {"errcode": -1, "errmsg": str(e)}
