from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.merchant import Merchant
from app.models.brand_asset import BrandAsset

router = APIRouter()


class MerchantRegisterRequest(BaseModel):
    name: str
    industry_context: str
    brand_symbol: Optional[str] = None


class MerchantProfileUpdate(BaseModel):
    name: Optional[str] = None
    industry_context: Optional[str] = None
    brand_symbol: Optional[str] = None


class BrandAssetUploadRequest(BaseModel):
    logo_url: str
    watermark_config: Optional[str] = None


@router.post("/register")
async def register_merchant(
    payload: MerchantRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    merchant = Merchant(
        name=payload.name,
        industry_context=payload.industry_context,
        brand_symbol=payload.brand_symbol,
    )
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)

    return {
        "code": 200,
        "msg": "Merchant registered",
        "data": {
            "merchant_id": merchant.id,
            "name": merchant.name,
            "industry_context": merchant.industry_context,
        },
    }


@router.put("/{merchant_id}/profile")
async def update_profile(
    merchant_id: str,
    payload: MerchantProfileUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    if payload.name is not None:
        merchant.name = payload.name
    if payload.industry_context is not None:
        merchant.industry_context = payload.industry_context
    if payload.brand_symbol is not None:
        merchant.brand_symbol = payload.brand_symbol

    await db.commit()
    await db.refresh(merchant)

    return {
        "code": 200,
        "msg": "Profile updated",
        "data": {
            "merchant_id": merchant.id,
            "name": merchant.name,
            "industry_context": merchant.industry_context,
        },
    }


@router.post("/{merchant_id}/brand-asset")
async def upload_brand_asset(
    merchant_id: str,
    payload: BrandAssetUploadRequest,
    db: AsyncSession = Depends(get_db),
):
    # 验证 merchant 存在
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    import uuid
    asset = BrandAsset(
        id=f"asset_{uuid.uuid4().hex[:10]}",
        merchant_id=merchant_id,
        logo_url=payload.logo_url,
        watermark_config=payload.watermark_config,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return {
        "code": 200,
        "msg": "Brand asset uploaded",
        "data": {
            "asset_id": asset.id,
            "merchant_id": asset.merchant_id,
            "logo_url": asset.logo_url,
        },
    }


@router.get("/{merchant_id}")
async def get_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    return {
        "code": 200,
        "msg": "Success",
        "data": {
            "merchant_id": merchant.id,
            "name": merchant.name,
            "industry_context": merchant.industry_context,
            "brand_symbol": merchant.brand_symbol,
            "created_at": merchant.created_at.isoformat() if merchant.created_at else None,
        },
    }
