import asyncio
from sqlalchemy import select
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import User

async def list_all():
    async with async_session_maker() as session:
        result = await session.execute(select(User.email, User.nome, User.id))
        users = result.fetchall()
        for u in users:
            print(u)

asyncio.run(list_all())
