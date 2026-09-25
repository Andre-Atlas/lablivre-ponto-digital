from fastapi.testclient import TestClient
from app.main import app
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import User, TipoUsuario
import uuid
import asyncio

async def add_user():
    async with async_session_maker() as db:
        new_user = User(
            id=uuid.uuid4(),
            email="pendente@example.com",
            nome="Aluno Pendente",
            tipo=TipoUsuario.ALUNO,
            turma_ou_equipe="Turma A",
            oauth_provider="google",
            oauth_sub="123456",
            ativo=True,
            admin_aprovado=False
        )
        db.add(new_user)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(add_user())
    print("User added!")
