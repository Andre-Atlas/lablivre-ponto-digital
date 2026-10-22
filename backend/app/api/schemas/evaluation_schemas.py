from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


# ── Learning Outcome catalog ──────────────────────────────────────────────
class LearningOutcomeOut(BaseModel):
    id: UUID
    numero: int
    nome: str
    descricao: str | None = None
    ativo: bool
    ordem: int


class LearningOutcomeInput(BaseModel):
    numero: int = Field(ge=1)
    nome: str
    descricao: str | None = None
    ordem: int | None = None


class LearningOutcomeUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    ativo: bool | None = None
    ordem: int | None = None


# ── Program config ────────────────────────────────────────────────────────
class ProgramConfig(BaseModel):
    data_inicio: date | None = None
    num_semanas: int
    semana_atual: int | None = None


# ── Evaluation ────────────────────────────────────────────────────────────
class Prefill(BaseModel):
    semana: int
    niveis: dict[UUID, int]


class EvaluationInput(BaseModel):
    user_id: UUID
    semana: int = Field(ge=1)
    niveis: dict[UUID, int] = Field(default_factory=dict)
    comentario: str | None = None


class EvaluationLevelOut(BaseModel):
    lo_id: UUID
    numero: int | None = None
    nome: str | None = None
    nivel: int
    mentor_id: UUID | None = None


class EvaluationCommentOut(BaseModel):
    mentor_id: UUID | None = None
    mentor_nome: str
    texto: str


class EvaluationOut(BaseModel):
    user_id: UUID
    user_nome: str | None = None
    semana: int
    turma: str
    niveis: list[EvaluationLevelOut] = []
    comentarios: list[EvaluationCommentOut] = []


# ── Dashboard ─────────────────────────────────────────────────────────────
class PendingStudent(BaseModel):
    user_id: UUID
    nome: str


class MentorCount(BaseModel):
    mentor_nome: str
    alunos_avaliados: int


class HeatmapRow(BaseModel):
    lo_id: UUID
    numero: int
    nome: str
    contagem: list[int]  # [count nível1, 2, 3, 4]


class Regression(BaseModel):
    user_id: UUID
    nome: str
    lo_id: UUID
    numero: int
    nivel_atual: int
    nivel_anterior: int


class Dashboard(BaseModel):
    turma: str
    semana: int
    total_alunos: int
    avaliados: int
    pendentes: list[PendingStudent] = []
    por_mentor: list[MentorCount] = []
    heatmap: list[HeatmapRow] = []
    regressoes: list[Regression] = []
