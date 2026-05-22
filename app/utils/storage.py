from pathlib import Path
import uuid
from fastapi import UploadFile
from app.core.config import get_settings

settings = get_settings()


async def save_upload(file: UploadFile, subfolder: str = "uploads") -> dict:
    """保存上传文件到本地存储，返回文件信息"""
    storage_path = Path(settings.STORAGE_PATH) / subfolder
    storage_path.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名
    file_ext = Path(file.filename).suffix if file.filename else ".bin"
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = storage_path / unique_name

    content = await file.read()
    file_path.write_bytes(content)

    return {
        "filename": unique_name,
        "original_name": file.filename,
        "path": str(file_path),
        "url": f"{settings.BASE_URL}/static/uploads/{subfolder}/{unique_name}",
        "size": len(content),
    }


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        Path(file_path).unlink(missing_ok=True)
        return True
    except Exception:
        return False
