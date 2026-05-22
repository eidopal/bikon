from fastapi.testclient import TestClient


def test_register_merchant(client):
    """测试注册商户"""
    payload = {
        "name": "Test Salon",
        "industry_context": "Hair salon in Shanghai",
    }
    resp = client.post("/api/v1/merchant/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert "merchant_id" in data["data"]


def test_get_merchant_not_found(client):
    """测试获取不存在的商户"""
    resp = client.get("/api/v1/merchant/mer_999999")
    assert resp.status_code == 404


def test_update_merchant_profile(client):
    """测试更新商户信息"""
    # 先注册
    payload = {
        "name": "Test Salon",
        "industry_context": "Hair salon",
    }
    resp = client.post("/api/v1/merchant/register", json=payload)
    merchant_id = resp.json()["data"]["merchant_id"]

    # 更新
    update_payload = {
        "name": "Updated Salon",
        "industry_context": "Updated context",
    }
    resp = client.put(f"/api/v1/merchant/{merchant_id}/profile", json=update_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["name"] == "Updated Salon"


def test_list_brand_assets(client):
    """测试列出品牌资产"""
    # 先注册商户
    payload = {
        "name": "Test Salon",
        "industry_context": "Hair salon",
    }
    resp = client.post("/api/v1/merchant/register", json=payload)
    merchant_id = resp.json()["data"]["merchant_id"]

    # 查询资产列表（应该为空）
    resp = client.get(f"/api/v1/merchant/{merchant_id}/brand-assets")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["data"] == []
