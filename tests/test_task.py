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


def test_health_check(client):
    """测试健康检查"""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "service" in data["data"]
    assert data["data"]["service"] == "bikon-api"
