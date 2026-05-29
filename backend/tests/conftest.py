import os
import pytest_asyncio
from fastapi import Depends
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.auth_deps import get_current_user
from app.core.context import Meter, set_meter
from app.core.database import get_db
from app.models.base import Base
from app.models.tenancy import Organization, User

# A seeded tenant used by the dependency override so existing endpoint tests
# (which don't send a JWT) run authenticated against a real org. Tests that
# exercise real auth/metering pop the override via the `real_auth` fixture.
TEST_ORG_ID = 1
TEST_USER_ID = 1

TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_app_test",
)

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)


async def override_get_db():
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


async def override_get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    user = await db.get(User, TEST_USER_ID)
    set_meter(Meter(org_id=TEST_ORG_ID, db=db, feature="test"))
    return user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # No explicit ids: on a freshly-created schema the sequences start at 1, so
    # the seeded org/user get id=1 while keeping the sequence consistent for
    # rows that tests insert later (e.g. register()).
    async with AsyncSession(test_engine, expire_on_commit=False) as s:
        s.add(Organization(name="Test Org"))
        await s.flush()
        s.add(
            User(
                org_id=TEST_ORG_ID,
                email="test@example.com",
                hashed_password="x",
                role="owner",
            )
        )
        await s.commit()
    set_meter(None)
    yield
    set_meter(None)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def real_auth():
    """Temporarily remove the auth override so a test exercises real JWT validation."""
    app.dependency_overrides.pop(get_current_user, None)
    yield
    app.dependency_overrides[get_current_user] = override_get_current_user


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
