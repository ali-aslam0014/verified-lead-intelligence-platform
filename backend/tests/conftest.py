import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.main import app


@pytest.fixture(scope="function")
def async_db_engine():
    """Create a fresh NullPool async engine for each test function to avoid loop reuse issues."""
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    yield engine
    # Cleanup


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


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client
