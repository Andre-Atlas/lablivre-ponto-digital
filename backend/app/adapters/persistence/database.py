from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
import os

# Por padrão vai usar o sqlite para testes locais se DATABASE_URL não existir
from app.config import settings
DATABASE_URL = settings.DATABASE_URL or "sqlite+aiosqlite:///./ponto_digital.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    # config especifica para sqlite (evitar lock de threads assincronas)
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency do FastAPI para obter uma sessão de banco de dados assíncrona.
    """
    async with async_session_maker() as session:
        yield session
