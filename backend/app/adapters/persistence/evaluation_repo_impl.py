import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.persistence.orm_models import EvaluationComment as CommentORM
from app.adapters.persistence.orm_models import EvaluationLevel as LevelORM
from app.adapters.persistence.orm_models import WeeklyEvaluation as EvaluationORM
from app.domain.models import (
    EvaluationComment,
    EvaluationLevel,
    WeeklyEvaluation,
)
from app.domain.ports.evaluation_repository import EvaluationRepository


class EvaluationRepositoryImpl(EvaluationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def obter(self, user_id: UUID, semana: int) -> WeeklyEvaluation | None:
        orm = await self._load_orm(user_id, semana)
        return self._to_domain(orm) if orm else None

    async def upsert(
        self,
        *,
        user_id: UUID,
        semana: int,
        turma: str,
        niveis: dict[UUID, int],
        mentor_id: UUID | None,
        mentor_nome: str | None,
        comentario: str | None,
    ) -> WeeklyEvaluation:
        orm = await self._load_orm(user_id, semana)
        if orm is None:
            orm = EvaluationORM(id=uuid.uuid4(), user_id=user_id, semana=semana, turma=turma)
            self.session.add(orm)
            await self.session.flush()
            by_lo: dict[UUID, LevelORM] = {}
            by_mentor: dict[UUID | None, CommentORM] = {}
        else:
            # Relationships are eagerly loaded by _load_orm (selectinload).
            by_lo = {lvl.lo_id: lvl for lvl in orm.niveis}
            by_mentor = {c.mentor_id: c for c in orm.comentarios}
        for lo_id, nivel in niveis.items():
            existing = by_lo.get(lo_id)
            if existing is not None:
                existing.nivel = nivel
                existing.mentor_id = mentor_id
            else:
                self.session.add(
                    LevelORM(
                        id=uuid.uuid4(),
                        evaluation_id=orm.id,
                        lo_id=lo_id,
                        nivel=nivel,
                        mentor_id=mentor_id,
                    )
                )

        # Substitui apenas o comentário do mentor informado
        if comentario is not None and comentario.strip():
            existing_c = by_mentor.get(mentor_id)
            if existing_c is not None:
                existing_c.texto = comentario
                existing_c.mentor_nome = mentor_nome or existing_c.mentor_nome
            else:
                self.session.add(
                    CommentORM(
                        id=uuid.uuid4(),
                        evaluation_id=orm.id,
                        mentor_id=mentor_id,
                        mentor_nome=mentor_nome or "",
                        texto=comentario,
                    )
                )

        await self.session.commit()
        reloaded = await self._load_orm(user_id, semana)
        assert reloaded is not None
        return self._to_domain(reloaded)

    async def niveis_do_aluno(self, user_id: UUID) -> list[tuple[int, UUID, int]]:
        stmt = (
            select(EvaluationORM.semana, LevelORM.lo_id, LevelORM.nivel)
            .join(LevelORM, LevelORM.evaluation_id == EvaluationORM.id)
            .where(EvaluationORM.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1], row[2]) for row in result.all()]

    async def listar_por_turma_semana(self, turma: str, semana: int) -> list[WeeklyEvaluation]:
        stmt = (
            select(EvaluationORM)
            .where(EvaluationORM.turma == turma, EvaluationORM.semana == semana)
            .options(selectinload(EvaluationORM.niveis), selectinload(EvaluationORM.comentarios))
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(o) for o in result.scalars().all()]

    async def _load_orm(self, user_id: UUID, semana: int) -> EvaluationORM | None:
        stmt = (
            select(EvaluationORM)
            .where(EvaluationORM.user_id == user_id, EvaluationORM.semana == semana)
            .options(selectinload(EvaluationORM.niveis), selectinload(EvaluationORM.comentarios))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    def _to_domain(self, orm: EvaluationORM) -> WeeklyEvaluation:
        return WeeklyEvaluation(
            id=orm.id,
            user_id=orm.user_id,
            semana=orm.semana,
            turma=orm.turma,
            criado_em=orm.criado_em,
            atualizado_em=orm.atualizado_em,
            niveis=[
                EvaluationLevel(
                    id=lvl.id,
                    evaluation_id=lvl.evaluation_id,
                    lo_id=lvl.lo_id,
                    nivel=lvl.nivel,
                    mentor_id=lvl.mentor_id,
                    atualizado_em=lvl.atualizado_em,
                )
                for lvl in orm.niveis
            ],
            comentarios=[
                EvaluationComment(
                    id=c.id,
                    evaluation_id=c.evaluation_id,
                    mentor_id=c.mentor_id,
                    mentor_nome=c.mentor_nome,
                    texto=c.texto,
                    atualizado_em=c.atualizado_em,
                )
                for c in orm.comentarios
            ],
        )
