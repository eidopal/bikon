"""Unit tests for task_service async functions"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.task_service import submit_task, get_task_result, generate_task_id
from app.models.task import Task, TaskStatus


class TestGenerateTaskId:
    def test_prefix(self):
        tid = generate_task_id()
        assert tid.startswith("task_")

    def test_uniqueness(self):
        ids = [generate_task_id() for _ in range(100)]
        assert len(set(ids)) == 100

    def test_no_invalid_chars(self):
        tid = generate_task_id()
        assert "/" not in tid
        assert "\\" not in tid


class TestSubmitTask:
    @pytest.mark.asyncio
    async def test_creates_task_with_pending_status(self):
        """验证提交的任务状态为 PENDING"""
        mock_db = MagicMock(spec=AsyncSession)
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # suppress background task
        with patch("asyncio.create_task"):
            result = await submit_task(
                mock_db,
                {
                    "merchant_id": "mer_test",
                    "industry_context": "test salon",
                    "inputs": {"images": ["http://example.com/a.jpg"]},
                    "copywriting_targets": ["wechat_moments"],
                },
            )

        assert "task_id" in result
        assert result["estimated_wait_ms"] == 8500
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


class TestGetTaskResult:
    @pytest.fixture
    def mock_db(self):
        db = MagicMock(spec=AsyncSession)
        return db

    @pytest.mark.asyncio
    async def test_not_found(self, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await get_task_result(mock_db, "task_nonexist")
        assert result == {"task_status": "NOT_FOUND"}

    @pytest.mark.asyncio
    async def test_completed_task_returns_parsed_result(self, mock_db):
        task = Task(
            id="task_test",
            merchant_id="mer_1",
            status=TaskStatus.COMPLETED,
            result=json.dumps({"task_status": "COMPLETED", "copywriting": {"wechat_moments": {"text": "hello"}}}),
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute.return_value = mock_result

        result = await get_task_result(mock_db, "task_test")
        assert result["task_status"] == "COMPLETED"
        assert "copywriting" in result

    @pytest.mark.asyncio
    async def test_failed_task(self, mock_db):
        task = Task(
            id="task_fail",
            merchant_id="mer_1",
            status=TaskStatus.FAILED,
            result=json.dumps({"task_status": "FAILED", "error": "Something broke"}),
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute.return_value = mock_result

        result = await get_task_result(mock_db, "task_fail")
        assert result["task_status"] == "FAILED"

    @pytest.mark.asyncio
    async def test_processing_task_returns_status_only(self, mock_db):
        task = Task(
            id="task_proc",
            merchant_id="mer_1",
            status=TaskStatus.PROCESSING,
            result=None,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute.return_value = mock_result

        result = await get_task_result(mock_db, "task_proc")
        assert result == {"task_status": "PROCESSING"}

    @pytest.mark.asyncio
    async def test_pending_task(self, mock_db):
        task = Task(
            id="task_pend",
            merchant_id="mer_1",
            status=TaskStatus.PENDING,
            result=None,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute.return_value = mock_result

        result = await get_task_result(mock_db, "task_pend")
        assert result == {"task_status": "PENDING"}
