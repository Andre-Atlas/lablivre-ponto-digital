import asyncio

import asyncpg


async def main():
    try:
        conn = await asyncpg.connect(
            "postgresql://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@db.djvpkrevmkrpvfzinqev.supabase.co:5432/postgres"
        )
        print("Success direct 5432!")
        await conn.close()
    except Exception as e:
        print("Failed direct 5432:", e)


asyncio.run(main())
