import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_db():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT email FROM users"))
        print("Users:", [row[0] for row in res])
        res2 = await conn.execute(text("SELECT mac_address FROM devices"))
        print("Devices:", [row[0] for row in res2])
    await engine.dispose()

asyncio.run(test_db())
