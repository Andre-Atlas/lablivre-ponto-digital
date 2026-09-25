from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from uuid import UUID

from app.domain.ports.user_repository import UserRepository
from app.domain.models import User
from app.domain.enums import TipoUsuario
from app.adapters.persistence.orm_models import User as UserORM

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def buscar_por_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self.session.execute(stmt)
        user_orm = result.scalars().first()
        if not user_orm: return None
        return self._to_domain(user_orm)

    async def buscar_por_email(self, email: str) -> Optional[User]:
        stmt = select(UserORM).where(UserORM.email == email)
        result = await self.session.execute(stmt)
        user_orm = result.scalars().first()
        if not user_orm: return None
        return self._to_domain(user_orm)

    async def criar(self, user: User) -> User:
        user_orm = UserORM(
            id=user.id,
            email=user.email,
            nome=user.nome,
            tipo=user.tipo,
            turma_ou_equipe=user.turma_ou_equipe,
            oauth_provider=user.oauth_provider,
            oauth_sub=user.oauth_sub,
            patrimonio=user.patrimonio,
            ativo=user.ativo,
            admin_aprovado=user.admin_aprovado,
            criado_em=user.criado_em,
            atualizado_em=user.atualizado_em
        )
        self.session.add(user_orm)
        await self.session.flush()
        return user

    async def atualizar(self, user: User) -> User:
        stmt = select(UserORM).where(UserORM.id == user.id)
        result = await self.session.execute(stmt)
        user_orm = result.scalars().first()
        if user_orm:
            user_orm.ativo = user.ativo
            user_orm.admin_aprovado = user.admin_aprovado
            user_orm.patrimonio = user.patrimonio
            user_orm.atualizado_em = user.atualizado_em
            await self.session.flush()
        return user

    async def listar(self, tipo: Optional[TipoUsuario] = None, turma: Optional[str] = None) -> List[User]:
        stmt = select(UserORM)
        if tipo:
            stmt = stmt.where(UserORM.tipo == tipo)
        if turma:
            stmt = stmt.where(UserORM.turma_ou_equipe == turma)
        result = await self.session.execute(stmt)
        return [self._to_domain(u) for u in result.scalars().all()]

    def _to_domain(self, user_orm: UserORM) -> User:
        return User(
            id=user_orm.id,
            email=user_orm.email,
            nome=user_orm.nome,
            tipo=user_orm.tipo,
            turma_ou_equipe=user_orm.turma_ou_equipe,
            oauth_provider=user_orm.oauth_provider,
            oauth_sub=user_orm.oauth_sub,
            patrimonio=user_orm.patrimonio,
            ativo=user_orm.ativo,
            admin_aprovado=user_orm.admin_aprovado,
            criado_em=user_orm.criado_em,
            atualizado_em=user_orm.atualizado_em
        )
