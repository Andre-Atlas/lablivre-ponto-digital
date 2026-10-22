from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.orm_models import LearningOutcome as LearningOutcomeORM
from app.domain.models import LearningOutcome
from app.domain.ports.learning_outcome_repository import LearningOutcomeRepository


class LearningOutcomeRepositoryImpl(LearningOutcomeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def criar(self, lo: LearningOutcome) -> LearningOutcome:
        orm = LearningOutcomeORM(
            id=lo.id,
            numero=lo.numero,
            nome=lo.nome,
            descricao=lo.descricao,
            ativo=lo.ativo,
            ordem=lo.ordem,
            criado_em=lo.criado_em,
            atualizado_em=lo.atualizado_em,
        )
        self.session.add(orm)
        await self.session.commit()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def buscar_por_id(self, lo_id: UUID) -> LearningOutcome | None:
        result = await self.session.execute(
            select(LearningOutcomeORM).where(LearningOutcomeORM.id == lo_id)
        )
        orm = result.scalars().first()
        return self._to_domain(orm) if orm else None

    async def buscar_por_numero(self, numero: int) -> LearningOutcome | None:
        result = await self.session.execute(
            select(LearningOutcomeORM).where(LearningOutcomeORM.numero == numero)
        )
        orm = result.scalars().first()
        return self._to_domain(orm) if orm else None

    async def listar(self, incluir_inativos: bool = False) -> list[LearningOutcome]:
        stmt = select(LearningOutcomeORM)
        if not incluir_inativos:
            stmt = stmt.where(LearningOutcomeORM.ativo == True)  # noqa: E712
        stmt = stmt.order_by(LearningOutcomeORM.ordem, LearningOutcomeORM.numero)
        result = await self.session.execute(stmt)
        return [self._to_domain(o) for o in result.scalars().all()]

    async def atualizar(self, lo: LearningOutcome) -> LearningOutcome:
        result = await self.session.execute(
            select(LearningOutcomeORM).where(LearningOutcomeORM.id == lo.id)
        )
        orm = result.scalars().first()
        if orm is None:
            raise ValueError(f"LO {lo.id} não encontrado")
        orm.nome = lo.nome
        orm.descricao = lo.descricao
        orm.ativo = lo.ativo
        orm.ordem = lo.ordem
        await self.session.commit()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    def _to_domain(self, orm: LearningOutcomeORM) -> LearningOutcome:
        return LearningOutcome(
            id=orm.id,
            numero=orm.numero,
            nome=orm.nome,
            descricao=orm.descricao,
            ativo=orm.ativo,
            ordem=orm.ordem,
            criado_em=orm.criado_em,
            atualizado_em=orm.atualizado_em,
        )
