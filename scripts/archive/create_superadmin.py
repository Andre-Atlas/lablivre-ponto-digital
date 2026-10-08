import asyncio
import uuid
from sqlalchemy import select
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import User
from app.domain.enums import TipoUsuario, RoleAdmin
from app.utils.security import get_password_hash

async def create_superadmin():
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == 'andreaas2005@gmail.com'))
        user = result.scalars().first()
        if user:
            user.role = RoleAdmin.SUPER_ADMIN
            user.admin_aprovado = True
            if not user.senha_hash:
                user.senha_hash = get_password_hash("admin123")
            await session.commit()
            print("Usuário já existia. Promovido para SUPER_ADMIN com sucesso!")
        else:
            new_user = User(
                id=uuid.uuid4(),
                nome="Andre Admin",
                email="andreaas2005@gmail.com",
                tipo=TipoUsuario.STAFF,
                role=RoleAdmin.SUPER_ADMIN,
                turma_ou_equipe="Equipe Admin",
                oauth_provider="local",
                oauth_sub="local_admin",
                admin_aprovado=True,
                ativo=True,
                senha_hash=get_password_hash("admin123")
            )
            session.add(new_user)
            await session.commit()
            print("Novo usuário andreaas2005@gmail.com criado como SUPER_ADMIN! Senha: admin123")

asyncio.run(create_superadmin())
