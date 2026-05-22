from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


def test_wechat_login_invalid_code(client):
    """测试微信登录（无效code）"""
    with patch("app.services.wechat_service.httpx.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"errcode": 40029, "errmsg": "invalid code"}
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        payload = {"code": "invalid_code"}
        resp = client.post("/api/v1/wechat/code2session", json=payload)
        assert resp.status_code == 400


def test_msg_sec_check(client):
    """测试文本安全审查"""
    with patch("app.services.wechat_service.httpx.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        payload = {"content": "测试内容"}
        resp = client.post("/api/v1/wechat/msg-sec-check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200


def test_img_sec_check(client):
    """测试图片安全审查"""
    with patch("app.services.wechat_service.img_sec_check") as mock_check:
        mock_check.return_value = {"errcode": 0, "errmsg": "ok"}

        payload = {"image_url": "http://example.com/image.jpg"}
        resp = client.post("/api/v1/wechat/img-sec-check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
