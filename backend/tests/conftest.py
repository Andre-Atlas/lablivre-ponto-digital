from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import Settings, get_settings
from app.main import app


@pytest.fixture
def override_settings() -> Settings:
    """Fixture para sobrescrever configurações da aplicação durante a execução dos testes."""
    test_settings = Settings(
        ENVIRONMENT="test",
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/ponto_digital_test",
        JWT_SECRET_KEY="test-jwt-secret-key-for-testing",
        APP_VERSION="0.1.0-test",
    )
    # Sobrescreve as dependências da aplicação FastAPI
    app.dependency_overrides[get_settings] = lambda: test_settings
    return test_settings


@pytest_asyncio.fixture
async def async_client(override_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Fixture que fornece um cliente HTTP assíncrono (httpx.AsyncClient) para testes de endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()
