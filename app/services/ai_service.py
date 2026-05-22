import os
import base64
import httpx
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from typing import List, Dict

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)

MODEL = os.getenv("OPENROUTER_MODEL")


async def download_file(url: str) -> bytes:
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(url)
        response.raise_for_status()
        return response.content


def encode_image_base64(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


async def transcribe_audio(audio_url: str) -> str:
    """语音转文本（使用 GPT-4o 的音频理解能力）"""
    try:
        audio_bytes = await download_file(audio_url)
        audio_b64 = encode_image_base64(audio_bytes, "audio/mpeg")

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "请转写以下音频为纯文本，去除口语化干扰，输出干净的服务描述。"},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}},
                ],
            }],
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Audio transcription failed: {e}")
        return ""


async def generate_copywriting(
    image_urls: List[str],
    transcript: str,
    merchant_context: str,
    targets: List[str],
) -> Dict:
    """生成多平台营销文案"""
    # 构建图片内容
    image_parts = []
    for url in image_urls[:9]:
        try:
            img_bytes = await download_file(url)
            img_b64 = encode_image_base64(img_bytes, "image/jpeg")
            image_parts.append({
                "type": "image_url",
                "image_url": {"url": img_b64},
            })
        except Exception as e:
            print(f"Failed to load image {url}: {e}")

    # 构建提示词
    target_desc = []
    if "wechat_moments" in targets:
        target_desc.append("微信朋友圈版：人设克制、专业、带有人情味，侧重客情维护，100字以内")
    if "xiaohongshu" in targets:
        target_desc.append("小红书种草版：多Emoji互动、语气偏高能种草，300字以内，包含5-8个SEO热门标签")

    prompt = f"""你是专业营销文案助手。基于以下信息生成多平台营销文案。

门店背景：{merchant_context}
服务描述：{transcript}

请按以下JSON格式输出（仅输出JSON，不要其他内容）：
{{
  "wechat_moments": {{"text": "朋友圈文案"}},
  "xiaohongshu": {{"text": "小红书文案", "tags": ["#标签1", "#标签2"]}}
}}

要求：
{chr(10).join("- " + t for t in target_desc)}
"""

    messages = [{
        "role": "user",
        "content": [{"type": "text", "text": prompt}] + image_parts,
    }]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=800,
        )
        import json
        content = response.choices[0].message.content.strip()
        # 提取 JSON（可能包含 markdown 代码块）
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print(f"Copywriting generation failed: {e}")
        # 返回默认文案
        return {
            "wechat_moments": {"text": f"今日服务已完成，欢迎咨询预约 - {merchant_context}"},
            "xiaohongshu": {"text": f"分享今日服务成果，感谢信任", "tags": ["#美业", "#服务"]},
        }


async def analyze_image_for_watermark(image_url: str) -> Dict:
    """分析图片以确定水印位置（简化版）"""
    return {"main_subject_region": "bottom", "brightness": "light"}
