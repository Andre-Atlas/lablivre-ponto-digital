"""Cria (ou atualiza) um mentor administrador — o primeiro acesso de um deploy novo.

Como alunos não têm login e não há autocadastro, todo banco novo começa sem acesso.
Rode uma vez (no Shell do Render ou localmente apontando o DATABASE_URL para o Neon):

    python scripts/create_admin.py --email voce@exemplo.com --nome "Seu Nome" --senha "umaSenhaForte"

Requer a variável DATABASE_URL apontando para o banco de produção.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid
from datetime import UTC, datetime

# Garante que o pacote `app` seja encontrado independentemente do diretório de execução.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select  # noqa: E402

from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import User
from app.domain.enums import RoleAdmin, TipoUsuario
from app.utils.security import get_password_hash


async def main(email: str, nome: str, senha: str) -> None:
    now = datetime.now(UTC)
    async with async_session_maker() as s:
        user = (await s.execute(select(User).where(User.email == email))).scalars().first()
        if user:
            user.nome = nome
            user.senha_hash = get_password_hash(senha)
            user.tipo = TipoUsuario.STAFF
            user.role = RoleAdmin.SUPER_ADMIN
            user.ativo = True
            user.admin_aprovado = True
            user.atualizado_em = now
            acao = "atualizado"
        else:
            s.add(
                User(
                    id=uuid.uuid4(), email=email, nome=nome, tipo=TipoUsuario.STAFF,
                    role=RoleAdmin.SUPER_ADMIN, turma_ou_equipe="Administração",
                    oauth_provider="manual", oauth_sub=email,
                    senha_hash=get_password_hash(senha), ativo=True, admin_aprovado=True,
                    criado_em=now, atualizado_em=now,
                )
            )
            acao = "criado"
        await s.commit()
    print(f"Admin {acao}: {email}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Cria/atualiza um mentor SUPER_ADMIN.")
    p.add_argument("--email", required=True)
    p.add_argument("--nome", default="Admin")
    p.add_argument("--senha", required=True)
    args = p.parse_args()
    asyncio.run(main(args.email, args.nome, args.senha))
