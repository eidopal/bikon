import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import (
    encode_image_base64,
    generate_copywriting,
    analyze_image_for_watermark,
)


class TestEncodeImageBase64:
    def test_returns_data_uri_format(self):
        result = encode_image_base64(b"test", "image/jpeg")
        assert result.startswith("data:image/jpeg;base64,")

    def test_different_mime_types(self):
        result = encode_image_base64(b"test", "image/png")
        assert result.startswith("data:image/png;base64,")


class TestGenerateCopywriting:
    @pytest.fixture
    def mock_openai(self):
        with patch("app.services.ai_service.client.chat.completions.create") as mock:
            yield mock

    def test_successful_generation(self, mock_openai):
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"wechat_moments": {"text": "test wx"}, "xiaohongshu": {"text": "test xhs", "tags": ["#tag"]}}'))]
        )
        result = generate_copywriting(
            image_urls=[],
            transcript="test transcript",
            merchant_context="test salon",
            targets=["wechat_moments", "xiaohongshu"],
        )
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(result)
        assert result["wechat_moments"]["text"] == "test wx"
        assert result["xiaohongshu"]["text"] == "test xhs"
        assert "#tag" in result["xiaohongshu"]["tags"]

    def test_extracts_json_from_markdown_block(self, mock_openai):
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='```json\n{"wechat_moments": {"text": "md wx"}, "xiaohongshu": {"text": "md xhs", "tags": ["#test"]}}\n```'))]
        )
        result = generate_copywriting(
            image_urls=[],
            transcript="",
            merchant_context="",
            targets=["wechat_moments", "xiaohongshu"],
        )
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(result)
        assert result["wechat_moments"]["text"] == "md wx"

    def test_fallback_on_api_error(self, mock_openai):
        mock_openai.side_effect = Exception("API error")
        result = generate_copywriting(
            image_urls=[],
            transcript="",
            merchant_context="test salon",
            targets=["wechat_moments", "xiaohongshu"],
        )
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(result)
        assert "wechat_moments" in result
        assert "xiaohongshu" in result

    def test_fallback_on_malformed_json(self, mock_openai):
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="not valid json at all"))]
        )
        result = generate_copywriting(
            image_urls=[],
            transcript="",
            merchant_context="test salon",
            targets=["wechat_moments", "xiaohongshu"],
        )
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(result)
        assert "wechat_moments" in result


class TestAnalyzeImageForWatermark:
    def test_returns_expected_structure(self):
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            analyze_image_for_watermark("http://example.com/img.jpg")
        )
        assert "main_subject_region" in result
        assert "brightness" in result
