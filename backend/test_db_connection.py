import asyncio

import asyncpg


async def main():
    dsn = "postgresql://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
    print(f"Connecting to {dsn}...")
    try:
        conn = await asyncpg.connect(dsn)
        print("Success!")
        await conn.close()
    except Exception as e:
        print(f"Failed: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
