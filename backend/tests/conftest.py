import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.core.database import get_db
from app.main import app


@pytest.fixture(scope="function")
def async_db_engine():
    """Create a fresh NullPool async engine for each test function to avoid loop reuse issues."""
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    yield engine


@pytest_asyncio.fixture(scope="function")
def async_session(async_db_engine):
    """Provide an isolated async session for database integration tests."""
    session_factory = async_sessionmaker(
        bind=async_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    return session_factory


@pytest_asyncio.fixture(scope="function")
async def async_client(async_session):
    async def _override_get_db():
        async with async_session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client
    app.dependency_overrides.clear()
