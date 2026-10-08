import asyncio

import asyncpg


async def check(port):
    dsn = f"postgresql://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:{port}/postgres?sslmode=require"
    print(f"Connecting to port {port}...")
    try:
        conn = await asyncio.wait_for(asyncpg.connect(dsn), timeout=10)
        print(f"Success on port {port}!")
        await conn.close()
    except Exception as e:
        print(f"Failed on port {port}: {type(e).__name__}: {e}")


async def main():
    await check(5432)
    await check(6543)


if __name__ == "__main__":
    asyncio.run(main())
