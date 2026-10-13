from __future__ import annotations

"""Caso de uso de gestão do catálogo de Learning Outcomes (LOs)."""

import uuid
from datetime import UTC, datetime
from uuid import UUID

from app.domain.models import LearningOutcome
from app.domain.ports.learning_outcome_repository import LearningOutcomeRepository


class LOValidationError(Exception):
    """Erro de validação de LO (número duplicado, dados inválidos)."""


class LONotFoundError(Exception):
    """LO não encontrado."""


class LOCatalogUseCase:
    def __init__(self, repo: LearningOutcomeRepository) -> None:
        self.repo = repo

    async def listar(self, incluir_inativos: bool = False) -> list[LearningOutcome]:
        return await self.repo.listar(incluir_inativos=incluir_inativos)

    async def criar(
        self, numero: int, nome: str, descricao: str | None, ordem: int | None
    ) -> LearningOutcome:
        if numero < 1:
            raise LOValidationError("Número do LO deve ser >= 1.")
        if not nome or not nome.strip():
            raise LOValidationError("Nome do LO é obrigatório.")
        if await self.repo.buscar_por_numero(numero) is not None:
            raise LOValidationError(f"Já existe um LO com número {numero}.")
        agora = datetime.now(UTC)
        lo = LearningOutcome(
            id=uuid.uuid4(),
            numero=numero,
            nome=nome.strip(),
            descricao=descricao,
            ativo=True,
            ordem=ordem if ordem is not None else numero,
            criado_em=agora,
            atualizado_em=agora,
        )
        return await self.repo.criar(lo)

    async def atualizar(
        self,
        lo_id: UUID,
        *,
        nome: str | None,
        descricao: str | None,
        ativo: bool | None,
        ordem: int | None,
    ) -> LearningOutcome:
        lo = await self.repo.buscar_por_id(lo_id)
        if lo is None:
            raise LONotFoundError(str(lo_id))
        if nome is not None:
            if not nome.strip():
                raise LOValidationError("Nome do LO não pode ser vazio.")
            lo.nome = nome.strip()
        if descricao is not None:
            lo.descricao = descricao
        if ativo is not None:
            lo.ativo = ativo
        if ordem is not None:
            lo.ordem = ordem
        return await self.repo.atualizar(lo)
