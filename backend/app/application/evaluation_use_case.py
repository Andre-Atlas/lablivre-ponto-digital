from __future__ import annotations

"""Caso de uso de avaliação semanal de Learning Outcomes (LOs).

Isola a regra de negócio (validação, pré-preenchimento, dashboard, relatório) do transporte
(FastAPI) e da persistência (SQLAlchemy). Semana é um índice inteiro derivado da configuração
do programa na tabela `config`.
"""

from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

from app.domain.enums import TipoUsuario
from app.domain.models import (
    CFG_DATA_INICIO,
    CFG_NUM_SEMANAS,
    NUM_SEMANAS_PADRAO,
    LearningOutcome,
    WeeklyEvaluation,
    detectar_regressoes,
    niveis_anteriores,
    nivel_valido,
    semana_atual,
    semana_no_intervalo,
)
from app.domain.ports.config_repository import ConfigRepository
from app.domain.ports.evaluation_repository import EvaluationRepository
from app.domain.ports.learning_outcome_repository import LearningOutcomeRepository
from app.domain.ports.user_repository import UserRepository


class EvaluationValidationError(Exception):
    """Erro de validação de avaliação (semana fora de intervalo, nível inválido, LO inativo)."""


class StudentNotFoundError(Exception):
    """Aluno não encontrado."""


class TurmaScopeError(Exception):
    """Mentor não pertence à turma do aluno."""


class EvaluationUseCase:
    def __init__(
        self,
        eval_repo: EvaluationRepository,
        lo_repo: LearningOutcomeRepository,
        user_repo: UserRepository,
        config_repo: ConfigRepository,
    ) -> None:
        self.eval_repo = eval_repo
        self.lo_repo = lo_repo
        self.user_repo = user_repo
        self.config_repo = config_repo

    # ── Program config ─────────────────────────────────────────────────────
    async def program_config(self, hoje: date | None = None) -> tuple[date | None, int, int | None]:
        raw_inicio = await self.config_repo.buscar(CFG_DATA_INICIO)
        raw_num = await self.config_repo.buscar(CFG_NUM_SEMANAS)
        num = int(raw_num) if raw_num else NUM_SEMANAS_PADRAO
        inicio = date.fromisoformat(raw_inicio) if raw_inicio else None
        atual = None
        if inicio is not None:
            atual = semana_atual(hoje or datetime.now(UTC).date(), inicio, num)
        return inicio, num, atual

    async def _num_semanas(self) -> int:
        _, num, _ = await self.program_config()
        return num

    # ── US1: record / get / prefill ────────────────────────────────────────
    async def registrar(
        self,
        *,
        user_id: UUID,
        mentor_id: UUID,
        mentor_turma: str,
        mentor_nome: str,
        semana: int,
        niveis: dict[UUID, int],
        comentario: str | None,
    ) -> tuple[WeeklyEvaluation, dict[UUID, LearningOutcome], str]:
        num_semanas = await self._num_semanas()
        if not semana_no_intervalo(semana, num_semanas):
            raise EvaluationValidationError(
                f"Semana {semana} fora do intervalo do programa (1..{num_semanas})."
            )
        student = await self.user_repo.buscar_por_id(user_id)
        if student is None:
            raise StudentNotFoundError(str(user_id))
        if student.tipo != TipoUsuario.ALUNO:
            raise EvaluationValidationError("Avaliações só se aplicam a alunos (ALUNO).")
        if student.turma_ou_equipe != mentor_turma:
            raise TurmaScopeError("Mentor não pertence à turma do aluno.")

        lo_map = {lo.id: lo for lo in await self.lo_repo.listar(incluir_inativos=False)}
        for lo_id, nivel in niveis.items():
            if lo_id not in lo_map:
                raise EvaluationValidationError(f"LO {lo_id} inexistente ou inativo.")
            if not nivel_valido(nivel):
                raise EvaluationValidationError(f"Nível {nivel} fora de 1–4 (LO {lo_id}).")

        evaluation = await self.eval_repo.upsert(
            user_id=user_id,
            semana=semana,
            turma=student.turma_ou_equipe,
            niveis=niveis,
            mentor_id=mentor_id,
            mentor_nome=mentor_nome,
            comentario=comentario,
        )
        return evaluation, lo_map, student.nome

    async def obter(
        self, user_id: UUID, semana: int
    ) -> tuple[WeeklyEvaluation | None, dict[UUID, LearningOutcome], str, str]:
        student = await self.user_repo.buscar_por_id(user_id)
        if student is None:
            raise StudentNotFoundError(str(user_id))
        evaluation = await self.eval_repo.obter(user_id, semana)
        lo_map = {lo.id: lo for lo in await self.lo_repo.listar(incluir_inativos=True)}
        return evaluation, lo_map, student.nome, student.turma_ou_equipe

    async def prefill(self, user_id: UUID, semana: int) -> dict[UUID, int]:
        rows = await self.eval_repo.niveis_do_aluno(user_id)
        return niveis_anteriores(rows, antes_de_semana=semana)

    async def turma_do_aluno(self, user_id: UUID) -> str | None:
        student = await self.user_repo.buscar_por_id(user_id)
        return student.turma_ou_equipe if student else None

    # ── US3: dashboard ──────────────────────────────────────────────────────
    async def dashboard(self, turma: str, semana: int) -> dict[str, Any]:
        students = await self.user_repo.listar(tipo=TipoUsuario.ALUNO, turma=turma, somente_ativos=True)
        evals = await self.eval_repo.listar_por_turma_semana(turma, semana)
        los = await self.lo_repo.listar(incluir_inativos=False)
        eval_by_user = {e.user_id: e for e in evals}

        def assessed(ev: WeeklyEvaluation | None) -> bool:
            return ev is not None and len(ev.niveis) > 0

        avaliados = [s for s in students if assessed(eval_by_user.get(s.id))]
        pendentes = [s for s in students if not assessed(eval_by_user.get(s.id))]

        # por_mentor: distinct students each mentor set >= 1 level for
        mentor_students: dict[UUID, set[UUID]] = {}
        for ev in evals:
            for lvl in ev.niveis:
                if lvl.mentor_id is not None:
                    mentor_students.setdefault(lvl.mentor_id, set()).add(ev.user_id)
        por_mentor = []
        for mentor_id, student_set in mentor_students.items():
            m = await self.user_repo.buscar_por_id(mentor_id)
            por_mentor.append(
                {"mentor_nome": m.nome if m else "—", "alunos_avaliados": len(student_set)}
            )

        # heatmap: per active LO, counts of levels 1-4
        heatmap = []
        for lo in los:
            counts = [0, 0, 0, 0]
            for ev in evals:
                for lvl in ev.niveis:
                    if lvl.lo_id == lo.id and 1 <= lvl.nivel <= 4:
                        counts[lvl.nivel - 1] += 1
            heatmap.append(
                {"lo_id": lo.id, "numero": lo.numero, "nome": lo.nome, "contagem": counts}
            )

        # regressions: per assessed student, compare current vs most recent prior
        lo_by_id = {lo.id: lo for lo in los}
        regressoes = []
        for s in avaliados:
            ev = eval_by_user[s.id]
            atuais = {lvl.lo_id: lvl.nivel for lvl in ev.niveis}
            rows = await self.eval_repo.niveis_do_aluno(s.id)
            anteriores = niveis_anteriores(rows, antes_de_semana=semana)
            for lo_id, atual, anterior in detectar_regressoes(atuais, anteriores):
                lo_obj = lo_by_id.get(lo_id)
                regressoes.append(
                    {
                        "user_id": s.id,
                        "nome": s.nome,
                        "lo_id": lo_id,
                        "numero": lo_obj.numero if lo_obj else 0,
                        "nivel_atual": atual,
                        "nivel_anterior": anterior,
                    }
                )

        return {
            "turma": turma,
            "semana": semana,
            "total_alunos": len(students),
            "avaliados": len(avaliados),
            "pendentes": [{"user_id": s.id, "nome": s.nome} for s in pendentes],
            "por_mentor": por_mentor,
            "heatmap": heatmap,
            "regressoes": regressoes,
        }

    # ── US4: report data ────────────────────────────────────────────────────
    async def dados_relatorio(self, turma: str, semana: int) -> dict[str, Any]:
        students = await self.user_repo.listar(tipo=TipoUsuario.ALUNO, turma=turma, somente_ativos=True)
        evals = await self.eval_repo.listar_por_turma_semana(turma, semana)
        los = await self.lo_repo.listar(incluir_inativos=False)
        eval_by_user = {e.user_id: e for e in evals}

        linhas = []
        for s in students:
            ev = eval_by_user.get(s.id)
            niveis_por_lo = {lvl.lo_id: lvl.nivel for lvl in ev.niveis} if ev else {}
            pendente = ev is None or len(ev.niveis) == 0
            comentarios = (
                "; ".join(f"[{c.mentor_nome}] {c.texto}" for c in ev.comentarios) if ev else ""
            )
            linhas.append(
                {
                    "nome": s.nome,
                    "email": s.email,
                    "pendente": pendente,
                    "niveis": [niveis_por_lo.get(lo.id) for lo in los],
                    "comentarios": comentarios,
                }
            )
        return {"turma": turma, "semana": semana, "los": los, "linhas": linhas}
