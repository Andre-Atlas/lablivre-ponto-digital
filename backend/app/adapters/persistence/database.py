from typing import Any
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

DATABASE_URL = settings.DATABASE_URL or "sqlite+aiosqlite:///./ponto_digital.db"

connect_args: dict[str, Any] = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False
elif "asyncpg" in DATABASE_URL:
    connect_args["statement_cache_size"] = 0

engine = create_async_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency do FastAPI para obter uma sessão de banco de dados assíncrona.
    """
    async with async_session_maker() as session:
        yield session
