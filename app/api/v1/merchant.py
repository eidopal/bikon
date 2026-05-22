from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.models.merchant import Merchant
from app.models.brand_asset import BrandAsset
from app.models.user import User
from app.core.auth import get_current_user
from app.utils.storage import save_upload, delete_file
from app.utils.response import success_response

router = APIRouter()


class MerchantRegisterRequest(BaseModel):
    name: str
    industry_context: str
    brand_symbol: Optional[str] = None


class MerchantProfileUpdate(BaseModel):
    name: Optional[str] = None
    industry_context: Optional[str] = None
    brand_symbol: Optional[str] = None


@router.post("/register")
async def register_merchant(
    payload: MerchantRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import uuid
    merchant = Merchant(
        id=f"mer_{uuid.uuid4().hex[:10]}",
        name=payload.name,
        industry_context=payload.industry_context,
        brand_symbol=payload.brand_symbol,
    )
    db.add(merchant)
    await db.flush()

    current_user.merchant_id = merchant.id
    await db.commit()
    await db.refresh(merchant)

    return success_response(
        data={
            "merchant_id": merchant.id,
            "name": merchant.name,
            "industry_context": merchant.industry_context,
            "user_id": current_user.id,
        },
        msg="Merchant registered",
    )


@router.put("/{merchant_id}/profile")
async def update_profile(
    merchant_id: str,
    payload: MerchantProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    return success_response(
        data={
            "merchant_id": merchant.id,
            "name": merchant.name,
            "industry_context": merchant.industry_context,
        },
        msg="Profile updated",
    )


@router.post("/{merchant_id}/brand-asset")
async def upload_brand_asset(
    merchant_id: str,
    file: UploadFile = File(...),
    asset_type: str = "logo",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 验证 merchant 存在
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # 保存文件
    file_info = await save_upload(file, subfolder=f"merchants/{merchant_id}")

    # 创建资产记录
    import uuid
    asset = BrandAsset(
        id=f"asset_{uuid.uuid4().hex[:10]}",
        merchant_id=merchant_id,
        asset_type=asset_type,
        file_path=file_info["path"],
        file_url=file_info["url"],
        original_name=file_info["original_name"],
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return success_response(
        data={
            "asset_id": asset.id,
            "merchant_id": asset.merchant_id,
            "asset_type": asset.asset_type,
            "file_url": asset.file_url,
            "original_name": asset.original_name,
        },
        msg="Brand asset uploaded",
    )


@router.get("/{merchant_id}/brand-assets")
async def list_brand_assets(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 验证 merchant 存在
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # 查询所有品牌资产
    stmt = select(BrandAsset).where(BrandAsset.merchant_id == merchant_id)
    result = await db.execute(stmt)
    assets = result.scalars().all()

    return success_response(
        data=[
            {
                "asset_id": a.id,
                "asset_type": a.asset_type,
                "file_url": a.file_url,
                "original_name": a.original_name,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in assets
        ],
        msg="Success",
    )


@router.delete("/{merchant_id}/brand-asset/{asset_id}")
async def delete_brand_asset(
    merchant_id: str,
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
    # 查询资产
    stmt = select(BrandAsset).where(
        BrandAsset.id == asset_id,
        BrandAsset.merchant_id == merchant_id,
    )
    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Brand asset not found")

    # 删除文件
    if asset.file_path:
        delete_file(asset.file_path)

    # 删除数据库记录
    await db.delete(asset)
    await db.commit()

    return success_response(msg="Brand asset deleted")


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

    return success_response(
        data={
            "merchant_id": merchant.id,
            "name": merchant.name,
            "industry_context": merchant.industry_context,
            "brand_symbol": merchant.brand_symbol,
            "created_at": merchant.created_at.isoformat() if merchant.created_at else None,
        },
        msg="Success",
    )


@router.get("/")
async def list_merchants(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """商户列表（分页）"""
    from sqlalchemy import func as sql_func

    stmt = (
        select(Merchant)
        .order_by(Merchant.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    merchants = result.scalars().all()

    count_stmt = select(sql_func.count(Merchant.id))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    return success_response(
        data={
            "merchants": [
                {
                    "merchant_id": m.id,
                    "name": m.name,
                    "industry_context": m.industry_context,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in merchants
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        msg="Success",
    )


@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除商户及其关联数据"""
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # 清理关联数据
    from app.models.task import Task
    from app.models.brand_asset import BrandAsset

    await db.execute(delete(BrandAsset).where(BrandAsset.merchant_id == merchant_id))
    await db.execute(delete(Task).where(Task.merchant_id == merchant_id))
    await db.delete(merchant)
    await db.commit()

    return success_response(msg="Merchant and associated data deleted")
