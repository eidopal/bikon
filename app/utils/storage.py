from pathlib import Path
from fastapi import UploadFile
from app.core.config import get_settings

settings = get_settings()


async def save_upload(file: UploadFile, subfolder: str = "uploads") -> str:
    """保存上传文件到本地存储"""
    storage_path = Path(settings.STORAGE_PATH) / subfolder
    storage_path.mkdir(parents=True, exist_ok=True)

    file_path = storage_path / file.filename
    content = await file.read()
    file_path.write_bytes(content)
    return str(file_path)
