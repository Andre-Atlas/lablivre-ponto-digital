import os
from collections.abc import AsyncGenerator

# Use a dedicated, isolated sqlite database for tests (never the dev ponto_digital.db).
# Must be set before importing app modules so the engine binds to it.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_lo_eval.db")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.adapters.persistence.database import engine  # noqa: E402
from app.adapters.persistence.orm_models import Base  # noqa: E402
from app.config import Settings, get_settings  # noqa: E402
from app.main import app  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def _create_tables() -> AsyncGenerator[None, None]:
    """Prepara o schema para cada teste.

    Em sqlite (execução local isolada) reinicia o schema antes de cada teste para total
    isolamento. Em Postgres (CI) NÃO derruba tabelas — o schema vem das migrações Alembic —
    para evitar operações destrutivas no banco de CI.
    """
    if engine.url.get_backend_name() == "sqlite":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    yield


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
