"""Autenticação — somente mentores (STAFF/ADMIN) autenticam. Alunos não têm login."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.adapters.auth.jwt_handler import create_access_token
from app.adapters.persistence.database import get_db
from app.adapters.persistence.orm_models import User as UserORM
from app.api.middleware.auth_dependencies import get_current_user
from app.api.schemas.auth_schemas import LoginRequest
from app.domain.enums import RoleAdmin, TipoUsuario
from app.utils.security import get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticação"])

_MENTOR_ROLES = {RoleAdmin.SUPER_ADMIN, RoleAdmin.ADMIN}


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> Any:
    result = await db.execute(select(UserORM).where(UserORM.email == request.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    if not user.senha_hash or not verify_password(request.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")
    if not user.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")

    # Só mentores (STAFF ou ADMIN/SUPER_ADMIN) acessam a plataforma — alunos não têm login.
    is_mentor = user.tipo == TipoUsuario.STAFF or user.role in _MENTOR_ROLES
    if not is_mentor:
        raise HTTPException(status_code=403, detail="Acesso restrito a mentores.")

    is_admin = user.role in _MENTOR_ROLES
    tipo_resposta = "ADMIN" if is_admin else user.tipo.value

    token = create_access_token(
        data={
            "sub": str(user.id),
            "tipo": tipo_resposta,
            "role": user.role.value if user.role else RoleAdmin.NONE.value,
        }
    )
    return {"access_token": token, "user_id": user.id, "tipo": tipo_resposta}


class UpdateNomeRequest(BaseModel):
    nome: str


@router.put("/me")
async def update_nome(
    request: UpdateNomeRequest,
    user_payload: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    user_id = user_payload["sub"]
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.nome = request.nome
    await db.commit()
    return {"message": "Nome atualizado com sucesso", "nome": user.nome}


class UpdateSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str


@router.put("/me/senha")
async def update_senha(
    request: UpdateSenhaRequest,
    user_payload: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    user_id = user_payload["sub"]
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if not user.senha_hash or not verify_password(request.senha_atual, user.senha_hash):
        raise HTTPException(status_code=401, detail="Senha atual incorreta")
    user.senha_hash = get_password_hash(request.nova_senha)
    await db.commit()
    return {"message": "Senha atualizada com sucesso"}
