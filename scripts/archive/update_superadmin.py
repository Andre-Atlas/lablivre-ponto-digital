import asyncio
from sqlalchemy import select
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import User
from app.domain.enums import RoleAdmin

async def make_superadmin():
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == 'andreaas2005@gmail.com'))
        user = result.scalars().first()
        if user:
            user.role = RoleAdmin.SUPER_ADMIN
            user.admin_aprovado = True
            await session.commit()
            print("Atualizado andreaas2005@gmail.com para SUPER_ADMIN")
        else:
            print("Usuário não encontrado.")

asyncio.run(make_superadmin())
