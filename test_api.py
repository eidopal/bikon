import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)

model = os.getenv("OPENROUTER_MODEL")
print("Testing OpenRouter API connection...")
print(f"Base URL: {os.getenv('OPENROUTER_BASE_URL')}")
print(f"Model: {model}")

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "请用中文回复：测试连接成功"}],
        max_tokens=50,
    )
    print("\nAPI Connection Successful!")
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model used: {response.model}")
except Exception as e:
    print(f"\nAPI Connection Failed: {e}")
