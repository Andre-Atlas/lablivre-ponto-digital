"""Caso de uso de frequência: lançar, atrelar/remover atestado."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from app.adapters.persistence.frequencia_repo_impl import (
    FrequenciaRepositoryImpl,
    FrequenciaValidationError,
)
from app.domain.enums import StatusFrequencia

_STATUS_LANCAVEIS = {StatusFrequencia.PRESENTE.value, StatusFrequencia.FALTA.value}


class FrequenciaUseCase:
    def __init__(self, repo: FrequenciaRepositoryImpl):
        self.repo = repo

    async def lancar(
        self,
        mentor_id: UUID,
        turma: str,
        data: date,
        turno: str,
        itens: list[tuple[UUID, str]],
    ) -> None:
        """Upsert idempotente de cada aluno. Só aceita PRESENTE/FALTA (Justificado deriva de atestado)."""
        for aluno_id, status in itens:
            if status not in _STATUS_LANCAVEIS:
                raise FrequenciaValidationError(
                    "Status inválido: use PRESENTE ou FALTA (Justificado vem do atestado)."
                )
            await self.repo.upsert(aluno_id, turma, data, turno, status, mentor_id)

    async def anexar_atestado(
        self, freq_id: UUID, documento: bytes, filename: str, content_type: str
    ) -> None:
        await self.repo.anexar_atestado(freq_id, documento, filename, content_type)

    async def remover_atestado(self, freq_id: UUID) -> None:
        await self.repo.remover_atestado(freq_id)
