import asyncio
import asyncpg

async def main():
    try:
        conn = await asyncpg.connect("postgresql://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres")
        print("Success without SSL!")
        await conn.close()
    except Exception as e:
        print("Failed without SSL:", e)

    try:
        conn = await asyncpg.connect("postgresql://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require")
        print("Success with SSL!")
        await conn.close()
    except Exception as e:
        print("Failed with SSL:", e)

asyncio.run(main())
