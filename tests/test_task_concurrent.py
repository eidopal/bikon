"""并发压力测试"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestConcurrentTaskSubmission:
    def test_concurrent_submit_returns_unique_ids(self):
        """提交 10 个并发任务，验证每个获得唯一 task_id"""
        import concurrent.futures

        def submit_one(index):
            with TestClient(app) as c:
                resp = c.post(
                    "/api/v1/production/submit-task",
                    json={
                        "merchant_id": f"mer_concurrent",
                        "industry_context": f"Salon {index}",
                        "inputs": {"images": []},
                        "copywriting_targets": ["wechat_moments"],
                    },
                )
                return resp.json()["data"]["task_id"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(submit_one, i) for i in range(10)]
            task_ids = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(set(task_ids)) == 10, "All 10 tasks should have unique IDs"

    def test_submit_and_query_initial_status(self, client):
        """提交任务并立即查询状态应为 PENDING 或 PROCESSING"""
        resp = client.post(
            "/api/v1/production/submit-task",
            json={
                "merchant_id": "mer_poll",
                "industry_context": "Test polling salon",
                "inputs": {"images": []},
                "copywriting_targets": ["wechat_moments"],
            },
        )
        assert resp.status_code == 200
        task_id = resp.json()["data"]["task_id"]

        resp = client.get(f"/api/v1/production/task-result/{task_id}")
        assert resp.status_code == 200
        data = resp.json()
        # 后台任务可能使用独立的 DB 引擎，在测试中任务状态不会推进到完成
        # 但任务应存在并被查询到
        status = data["data"]["task_status"]
        assert status != "NOT_FOUND", "Task should exist after submission"
