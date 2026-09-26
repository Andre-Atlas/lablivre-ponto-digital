import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require", connect_args={"statement_cache_size": 0})
    async with engine.connect() as conn:
        await conn.execute(text("UPDATE users SET role='SUPER_ADMIN', tipo='STAFF', admin_aprovado=true WHERE email='andreaas2005@gmail.com';"))
        await conn.execute(text("UPDATE users SET role='SUPER_ADMIN', tipo='STAFF', admin_aprovado=true WHERE email='admin@eldorado.org.br';"))
        await conn.commit()
        print("Updated super admins")
    await engine.dispose()

asyncio.run(main())
