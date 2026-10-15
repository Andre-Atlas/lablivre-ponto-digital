"""Porta (interface) do repositório de frequência."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any
from uuid import UUID


class FrequenciaRepository(ABC):
    @abstractmethod
    async def listar(self, turma: str, data: date, turno: str) -> list[Any]:
        """Lança os registros existentes para a turma/data/turno."""

    @abstractmethod
    async def upsert(
        self,
        aluno_id: UUID,
        turma: str,
        data: date,
        turno: str,
        status: str,
        mentor_id: UUID | None,
    ) -> Any:
        """Cria ou atualiza o lançamento de um aluno (idempotente por aluno/data/turno)."""

    @abstractmethod
    async def anexar_atestado(
        self, freq_id: UUID, documento: bytes, filename: str, content_type: str
    ) -> Any:
        """Anexa atestado a um lançamento de Falta → Justificado."""

    @abstractmethod
    async def remover_atestado(self, freq_id: UUID) -> Any:
        """Remove o atestado → volta a Falta."""

    @abstractmethod
    async def obter(self, freq_id: UUID) -> Any | None:
        ...
