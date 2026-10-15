"""Schemas Pydantic do lançamento de frequência."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel


class FrequenciaItemIn(BaseModel):
    aluno_id: UUID
    status: str  # PRESENTE | FALTA


class LancamentoIn(BaseModel):
    turma: str
    data: date
    turno: str  # MANHA | TARDE
    lancamentos: list[FrequenciaItemIn]


class AlunoFrequenciaOut(BaseModel):
    aluno_id: UUID
    aluno_nome: str
    freq_id: UUID | None = None
    status: str | None = None  # PRESENTE | FALTA | JUSTIFICADO | None (ainda não lançado)
    tem_atestado: bool = False
