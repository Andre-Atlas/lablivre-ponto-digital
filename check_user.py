import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, update
from app.adapters.persistence.orm_models import User as UserModel
from app.domain.enums import TipoUsuario

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require", connect_args={"statement_cache_size": 0})
    async with AsyncSession(engine) as session:
        result = await session.execute(select(UserModel).where(UserModel.email == 'andrealvesacioli@gmail.com'))
        user = result.scalars().first()
        if user:
            print("User found:", user.email, "Tipo:", user.tipo)
        else:
            print("User not found.")
    await engine.dispose()

asyncio.run(main())
