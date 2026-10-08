import asyncio
import uuid

from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import TipoUsuario, User
from app.utils.security import get_password_hash


async def seed():
    async with async_session_maker() as session:
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        user = result.scalar_one_or_none()
        hashed = get_password_hash("admin123")

        if not user:
            new_admin = User(
                email="admin@example.com",
                nome="Super Admin",
                tipo=TipoUsuario.STAFF,
                turma_ou_equipe="Administração",
                oauth_provider="manual",
                oauth_sub=f"manual_{uuid.uuid4()}",
                admin_aprovado=True,
                senha_hash=hashed,
            )
            session.add(new_admin)
            await session.commit()
            print("Admin seeded!")
        else:
            user.senha_hash = hashed
            await session.commit()
            print("Admin updated with password hash!")


if __name__ == "__main__":
    asyncio.run(seed())
