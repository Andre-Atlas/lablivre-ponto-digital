from __future__ import annotations

"""Interface de repositório do catálogo de Learning Outcomes (LOs)."""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models import LearningOutcome


class LearningOutcomeRepository(ABC):
    """Port para persistência do catálogo de LOs."""

    @abstractmethod
    async def criar(self, lo: LearningOutcome) -> LearningOutcome:
        """Cria um novo LO."""
        ...

    @abstractmethod
    async def buscar_por_id(self, lo_id: UUID) -> LearningOutcome | None:
        """Busca um LO pelo id."""
        ...

    @abstractmethod
    async def buscar_por_numero(self, numero: int) -> LearningOutcome | None:
        """Busca um LO pelo número (para checagem de unicidade)."""
        ...

    @abstractmethod
    async def listar(self, incluir_inativos: bool = False) -> list[LearningOutcome]:
        """Lista LOs ordenados por `ordem` (apenas ativos por padrão)."""
        ...

    @abstractmethod
    async def atualizar(self, lo: LearningOutcome) -> LearningOutcome:
        """Atualiza nome/descrição/ativo/ordem de um LO."""
        ...
