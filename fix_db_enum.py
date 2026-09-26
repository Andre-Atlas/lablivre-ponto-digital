import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require", connect_args={"statement_cache_size": 0})
    async with engine.connect() as conn:
        try:
            await conn.execute(text("ALTER TYPE roleadmin ADD VALUE 'NONE';"))
            await conn.commit()
            print("Enum altered successfully!")
        except Exception as e:
            print("Error altering enum:", e)
    await engine.dispose()

asyncio.run(main())
