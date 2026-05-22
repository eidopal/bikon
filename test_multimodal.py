import os
import base64
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from PIL import Image
import io

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)

model = os.getenv("OPENROUTER_MODEL")
print(f"Testing model: {model}")

# 生成本地测试图片
print("Creating local test image...")
img = Image.new('RGB', (200, 200), color='red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_byte_arr = img_byte_arr.getvalue()
img_b64 = base64.b64encode(img_byte_arr).decode()

print(f"Image size: {len(img_byte_arr)} bytes")
print("Sending image + text to model...\n")

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "请描述这张图片的内容，用中文回答"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            ],
        }],
        max_tokens=200,
    )
    print("Multimodal Test Successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Multimodal Test Failed: {e}")
