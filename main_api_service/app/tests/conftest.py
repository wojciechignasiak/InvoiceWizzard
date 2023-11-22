import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
import redis

@pytest.fixture
def mock_postgres_async_session():
    yield AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_redis_client():
    yield Mock(spec=redis.Redis)