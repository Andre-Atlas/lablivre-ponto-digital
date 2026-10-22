from __future__ import annotations

"""Interface de repositório de avaliações semanais de LOs."""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models import WeeklyEvaluation


class EvaluationRepository(ABC):
    """Port para persistência de avaliações semanais (níveis por LO + comentários)."""

    @abstractmethod
    async def obter(self, user_id: UUID, semana: int) -> WeeklyEvaluation | None:
        """Busca a avaliação de um aluno em uma semana (com níveis e comentários)."""
        ...

    @abstractmethod
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
        """Cria/atualiza a avaliação do aluno na semana.

        Faz upsert de cada nível por LO (last-write-wins, atribuído ao mentor) e substitui
        apenas o comentário do mentor informado. Retorna a avaliação resultante completa.
        """
        ...

    @abstractmethod
    async def niveis_do_aluno(self, user_id: UUID) -> list[tuple[int, UUID, int]]:
        """Todos os níveis do aluno como tuplas (semana, lo_id, nivel), para pré-preenchimento."""
        ...

    @abstractmethod
    async def listar_por_turma_semana(self, turma: str, semana: int) -> list[WeeklyEvaluation]:
        """Avaliações (com níveis e comentários) de uma turma em uma semana, para dashboard/relatório."""
        ...
