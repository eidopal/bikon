import pytest
import tempfile
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.main import app
from app.database import Base
from app.models.user import User


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Set up test database using a temporary file"""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    test_url = f"sqlite+aiosqlite:///{db_path}"
    test_engine = create_async_engine(test_url, echo=False)

    async def init_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())

    import app.database
    app.database.engine = test_engine
    app.database.AsyncSessionLocal = sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    yield

    try:
        loop.run_until_complete(test_engine.dispose())
        os.unlink(db_path)
        loop.close()
    except Exception:
        pass


@pytest.fixture(scope="session")
def test_user(setup_database):
    """Create a real test user in DB for auth override"""
    from app.database import AsyncSessionLocal

    async def _create_user():
        async with AsyncSessionLocal() as db:
            stmt = select(User).where(User.openid == "test_openid")
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if user is None:
                user = User(
                    id="user_test00000000",
                    openid="test_openid",
                    nickname="Test User",
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            return user

    return asyncio.run(_create_user())


@pytest.fixture
def client(test_user):
    """Create test client with auth override"""
    from app.core.auth import get_current_user

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
