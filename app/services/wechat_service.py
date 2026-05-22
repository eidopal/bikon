import httpx
from app.core.config import get_settings

settings = get_settings()


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


async def msg_sec_check(content: str) -> bool:
    """微信内容安全审查（文本）"""
    # 需要先获取 access_token，此处为占位实现
    return True


async def img_sec_check(image_data: bytes) -> bool:
    """微信内容安全审查（图片）"""
    # 需要先获取 access_token，此处为占位实现
    return True
