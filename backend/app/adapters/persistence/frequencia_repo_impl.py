"""Adaptador de persistência da frequência (lançamento pelo mentor)."""
from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.orm_models import Frequencia as FrequenciaORM
from app.domain.enums import StatusFrequencia


class FrequenciaRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar(self, turma: str, data: date, turno: str) -> list[FrequenciaORM]:
        stmt = select(FrequenciaORM).where(
            FrequenciaORM.turma == turma,
            FrequenciaORM.data == data,
            FrequenciaORM.turno == turno,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def obter(self, freq_id: UUID) -> FrequenciaORM | None:
        return (
            await self.session.execute(select(FrequenciaORM).where(FrequenciaORM.id == freq_id))
        ).scalars().first()

    async def upsert(
        self,
        aluno_id: UUID,
        turma: str,
        data: date,
        turno: str,
        status: str,
        mentor_id: UUID | None,
    ) -> FrequenciaORM:
        now = datetime.now(UTC)
        existing = (
            await self.session.execute(
                select(FrequenciaORM).where(
                    FrequenciaORM.aluno_id == aluno_id,
                    FrequenciaORM.data == data,
                    FrequenciaORM.turno == turno,
                )
            )
        ).scalars().first()

        if existing:
            existing.mentor_id = mentor_id
            existing.turma = turma
            existing.atualizado_em = now
            if status == StatusFrequencia.PRESENTE.value:
                # Presente limpa qualquer atestado atrelado.
                existing.status = StatusFrequencia.PRESENTE.value
                existing.atestado_documento = None
                existing.atestado_filename = None
                existing.atestado_content_type = None
            elif status == StatusFrequencia.FALTA.value:
                # Falta mantém Justificado se já houver atestado (o atestado prevalece).
                existing.status = (
                    StatusFrequencia.JUSTIFICADO.value
                    if existing.atestado_documento
                    else StatusFrequencia.FALTA.value
                )
            else:
                existing.status = status
            row = existing
        else:
            row = FrequenciaORM(
                aluno_id=aluno_id,
                turma=turma,
                data=data,
                turno=turno,
                status=status,
                mentor_id=mentor_id,
                criado_em=now,
                atualizado_em=now,
            )
            self.session.add(row)
        await self.session.flush()
        return row

    async def anexar_atestado(
        self, freq_id: UUID, documento: bytes, filename: str, content_type: str
    ) -> FrequenciaORM:
        row = await self.obter(freq_id)
        if row is None:
            raise FrequenciaNotFoundError
        if row.status == StatusFrequencia.PRESENTE.value:
            raise FrequenciaValidationError("Só é possível anexar atestado a uma falta.")
        row.atestado_documento = documento
        row.atestado_filename = filename
        row.atestado_content_type = content_type
        row.status = StatusFrequencia.JUSTIFICADO.value
        row.atualizado_em = datetime.now(UTC)
        await self.session.flush()
        return row

    async def remover_atestado(self, freq_id: UUID) -> FrequenciaORM:
        row = await self.obter(freq_id)
        if row is None:
            raise FrequenciaNotFoundError
        row.atestado_documento = None
        row.atestado_filename = None
        row.atestado_content_type = None
        row.status = StatusFrequencia.FALTA.value
        row.atualizado_em = datetime.now(UTC)
        await self.session.flush()
        return row


class FrequenciaNotFoundError(Exception):
    pass


class FrequenciaValidationError(Exception):
    pass
