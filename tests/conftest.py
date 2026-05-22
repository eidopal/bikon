import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio

from app.main import app
from app.database import Base, engine as original_engine


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Set up test database using a temporary file"""
    # Create a temporary database file
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    # Create test engine
    test_url = f"sqlite+aiosqlite:///{db_path}"
    test_engine = create_async_engine(test_url, echo=False)

    # Create tables
    async def init_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    # Override the app's database engine and sessionmaker
    import app.database
    app.database.engine = test_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    app.database.AsyncSessionLocal = sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    yield

    # Cleanup
    try:
        loop.run_until_complete(test_engine.dispose())
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as c:
        yield c
