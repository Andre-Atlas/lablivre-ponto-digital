import asyncio
import asyncpg
import sys


async def check(host, port):
    dsn = f"postgresql://postgres:J.4_jkbaKyDe3XK@{host}:{port}/postgres?sslmode=require"
    print(f"Connecting to {host}:{port}...")
    try:
        conn = await asyncio.wait_for(asyncpg.connect(dsn), timeout=5)
        print(f"Success on {host}:{port}!")
        await conn.close()
    except Exception as e:
        print(f"Failed on {host}:{port}: {type(e).__name__}: {e}")


async def main():
    await check("db.djvpkrevmkrpvfzinqev.supabase.co", 5432)
    await check("db.djvpkrevmkrpvfzinqev.supabase.co", 6543)


if __name__ == "__main__":
    asyncio.run(main())
