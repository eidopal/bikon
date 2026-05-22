import httpx
import json
import time
import sys

BASE_URL = "http://localhost:8000"

TEST_IMAGE = "https://images.unsplash.com/photo-1522337660859-1958410efocus5?w=400"

print("=== BIKON Complete Workflow Test ===\n")

# 1. Submit task
print("[1/3] Submitting production task...")
payload = {
    "merchant_id": "mer_8848",
    "industry_context": "Shanghai Jingan light luxury Japanese salon, 150-300 yuan per customer",
    "inputs": {
        "images": [TEST_IMAGE],
        "audio_url": ""
    },
    "visual_config": {
        "watermark_type": "dynamic_brand",
        "brand_symbol": "BIKON",
        "symbol_variant": "beacon_tower_i",
        "watermark_position": "auto_detect"
    },
    "copywriting_targets": ["wechat_moments", "xiaohongshu"]
}

try:
    resp = httpx.post(f"{BASE_URL}/api/v1/production/submit-task", json=payload, timeout=10)
    print(f"Submit status: {resp.status_code}")
    result = resp.json()
    print(json.dumps(result, ensure_ascii=False, indent=2))

    task_id = result.get("data", {}).get("task_id")
    if not task_id:
        print("[X] Failed to get task_id")
        sys.exit(1)
    print(f"\n[OK] Task submitted, ID: {task_id}")
except Exception as e:
    print(f"[X] Submit failed: {e}")
    sys.exit(1)

# 2. Poll for result
print(f"\n[2/3] Waiting for task processing (about 15 seconds)...")
for i in range(10):
    time.sleep(2)
    try:
        resp = httpx.get(f"{BASE_URL}/api/v1/production/task-result/{task_id}", timeout=10)
        data = resp.json()
        status = data.get("data", {}).get("task_status", "UNKNOWN")
        print(f"  [{i+1}] Status: {status}")

        if status == "COMPLETED":
            print(f"\n[OK] Task completed!\n")
            print("=== Generated Results ===")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            break
        elif status == "FAILED":
            print(f"\n[X] Task failed!")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            break
    except Exception as e:
        print(f"  Query failed: {e}")

print(f"\n[3/3] Test completed!")
