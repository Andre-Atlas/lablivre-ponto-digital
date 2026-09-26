import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from app.adapters.persistence.orm_models import User as UserModel, Checkin as CheckInModel

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require", connect_args={"statement_cache_size": 0})
    async with engine.connect() as conn:
        result = await conn.execute(
            select(CheckInModel, UserModel)
            .join(UserModel, CheckInModel.user_id == UserModel.id)
            .order_by(CheckInModel.hora_checkin.desc())
        )
        rows = result.all()
        print(len(rows))
        if len(rows) > 0:
            print(rows[0])
            print(len(rows[0]))
    await engine.dispose()

asyncio.run(main())
