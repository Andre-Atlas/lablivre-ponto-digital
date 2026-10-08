import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from app.adapters.persistence.orm_models import User
import os

async def main():
    db_url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require")
    engine = create_async_engine(db_url)
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == "andreaas2005@gmail.com"))
        user = result.scalars().first()
        print(f"User: {user.email}, Tipo: {user.tipo}, Role: {user.role}")

asyncio.run(main())
