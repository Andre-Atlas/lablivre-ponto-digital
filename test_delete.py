import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from app.adapters.persistence.orm_models import User as UserModel

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require", connect_args={"statement_cache_size": 0})
    async with AsyncSession(engine) as session:
        result = await session.execute(select(UserModel).where(UserModel.email == 'andrealvesacioli@gmail.com'))
        user = result.scalars().first()
        if user:
            print("Deleting user:", user.email)
            await session.delete(user)
            try:
                await session.commit()
                print("Delete successful!")
            except Exception as e:
                print("Delete failed:", e)
        else:
            print("User not found.")
    await engine.dispose()

asyncio.run(main())
