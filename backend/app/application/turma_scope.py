"""Escopo de turmas de um mentor (RBAC por turma)."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.orm_models import MentorTurma
from app.adapters.persistence.orm_models import User as UserModel
from app.domain.enums import RoleAdmin

_ADMIN_ROLES = {RoleAdmin.SUPER_ADMIN, RoleAdmin.ADMIN}


async def turmas_do_mentor(db: AsyncSession, user: UserModel) -> set[str] | None:
    """Conjunto de turmas às quais o mentor está atrelado.

    Retorna None para admin/super-admin (acesso a TODAS as turmas).
    """
    if user.role in _ADMIN_ROLES:
        return None
    rows = await db.execute(select(MentorTurma.turma).where(MentorTurma.user_id == user.id))
    return {r[0] for r in rows.all()}


async def assert_turma_permitida(db: AsyncSession, user: UserModel, turma: str) -> None:
    """403 se o mentor não estiver atrelado à turma (admin sempre passa)."""
    permitidas = await turmas_do_mentor(db, user)
    if permitidas is not None and turma not in permitidas:
        raise HTTPException(status_code=403, detail="Você não tem acesso a esta turma.")
