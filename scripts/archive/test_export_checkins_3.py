import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from app.adapters.persistence.orm_models import User as UserModel, Checkin as CheckInModel

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require", connect_args={"statement_cache_size": 0})
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(CheckInModel, UserModel)
            .join(UserModel, CheckInModel.user_id == UserModel.id)
            .order_by(CheckInModel.hora_checkin.desc())
        )
        rows = result.all()
        print(len(rows))
        if len(rows) > 0:
            row = rows[0]
            print(row)
            print(len(row))
            print(type(row[0]))
    await engine.dispose()

asyncio.run(main())
