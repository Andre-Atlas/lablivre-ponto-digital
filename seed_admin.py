import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.adapters.persistence.database import get_db
from app.utils.security import get_password_hash
from sqlalchemy import text
import uuid
import datetime

DATABASE_URL = "postgresql+asyncpg://postgres.djvpkrevmkrpvfzinqev:J.4_jkbaKyDe3XK@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?ssl=require"

async def seed():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        # Check if exists
        result = await session.execute(text("SELECT id FROM users WHERE email='admin@eldorado.org.br'"))
        row = result.fetchone()
        
        if not row:
            hashed_pw = get_password_hash('admin123')
            uid = str(uuid.uuid4())
            await session.execute(
                text("""
                INSERT INTO users (id, email, nome, tipo, turma_ou_equipe, oauth_provider, oauth_sub, ativo, admin_aprovado, senha_hash, criado_em, atualizado_em) 
                VALUES (:id, :email, :nome, 'STAFF', 'Administração', 'local', 'local', true, true, :senha, now(), now())
                """),
                {"id": uid, "email": "admin@eldorado.org.br", "nome": "Admin Principal", "senha": hashed_pw}
            )
            await session.commit()
            print("Admin created!")
        else:
            hashed_pw = get_password_hash('admin123')
            await session.execute(
                text("UPDATE users SET senha_hash=:senha WHERE email='admin@eldorado.org.br'"),
                {"senha": hashed_pw}
            )
            await session.commit()
            print("Admin updated with password!")

asyncio.run(seed())
