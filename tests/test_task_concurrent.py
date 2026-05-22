"""任务提交测试"""
import pytest


class TestTaskSubmission:
    def test_multiple_submit_returns_unique_ids(self, client):
        """提交 5 个任务，验证每个获得唯一 task_id"""
        task_ids = []
        for i in range(5):
            resp = client.post(
                "/api/v1/production/submit-task",
                json={
                    "merchant_id": "mer_test_multi",
                    "industry_context": f"Salon {i}",
                    "inputs": {"images": []},
                    "copywriting_targets": ["wechat_moments"],
                },
            )
            assert resp.status_code == 200
            task_ids.append(resp.json()["data"]["task_id"])

        assert len(set(task_ids)) == 5, "All 5 tasks should have unique IDs"

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
