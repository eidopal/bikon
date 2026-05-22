from fastapi.testclient import TestClient


def test_ping(client):
    """测试 ping 接口"""
    resp = client.get("/api/v1/production/ping")
    assert resp.status_code == 200
    assert resp.json()["pong"] is True


def test_submit_task(client):
    """测试提交任务"""
    payload = {
        "merchant_id": "mer_test",
        "industry_context": "Test salon",
        "inputs": {
            "images": [],
        },
        "copywriting_targets": ["wechat_moments"],
    }
    resp = client.post("/api/v1/production/submit-task", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert "task_id" in data["data"]


def test_get_task_result_not_found(client):
    """测试获取不存在的任务结果"""
    resp = client.get("/api/v1/production/task-result/task_notfound")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 404
    assert data["data"] is None


def test_submit_with_files(client):
    """测试上传文件提交任务"""
    from io import BytesIO

    fake_image = BytesIO()
    from PIL import Image
    Image.new("RGB", (10, 10), color="red").save(fake_image, format="JPEG")
    fake_image.seek(0)

    resp = client.post(
        "/api/v1/production/submit-with-files",
        files=[("files", ("test.jpg", fake_image.read(), "image/jpeg"))],
        data={
            "merchant_id": "mer_file_test",
            "industry_context": "Test salon for file upload",
            "copywriting_targets": "wechat_moments",
            "watermark_text": "TEST",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert "task_id" in data["data"]
    assert len(data["data"]["uploaded_images"]) == 1


def test_upload_image(client):
    """测试单张图片上传"""
    from io import BytesIO
    from PIL import Image

    fake_image = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(fake_image, format="JPEG")
    fake_image.seek(0)

    resp = client.post(
        "/api/v1/production/upload-image",
        files={"file": ("test.jpg", fake_image.read(), "image/jpeg")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"]["url"].startswith("http://")


def test_list_tasks(client):
    """测试任务列表"""
    # 先提交一个任务
    client.post(
        "/api/v1/production/submit-task",
        json={
            "merchant_id": "mer_list_test",
            "inputs": {"images": []},
            "copywriting_targets": ["wechat_moments"],
        },
    )

    resp = client.get("/api/v1/production/tasks", params={"merchant_id": "mer_list_test"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert "tasks" in data["data"]
    assert "total" in data["data"]
    assert data["data"]["total"] >= 1


def test_health_check(client):
    """测试健康检查"""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "service" in data["data"]
    assert data["data"]["service"] == "bikon-api"
