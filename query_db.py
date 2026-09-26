import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require", connect_args={"statement_cache_size": 0})
    async with engine.connect() as conn:
        print("--- USERS ---")
        users = await conn.execute(text("SELECT id, email, nome FROM users"))
        for u in users:
            print(u)
        
        print("\n--- DEVICES ---")
        devices = await conn.execute(text("SELECT id, user_id, mac_address FROM devices"))
        for d in devices:
            print(d)
    await engine.dispose()

asyncio.run(main())
