from __future__ import annotations

"""Interface de repositório de check-ins."""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models import CheckIn, CheckInDuplicata


class CheckInRepository(ABC):
    """Port para persistência de registros de ponto."""

    @abstractmethod
    async def buscar_por_turno(self, user_id: UUID, turno_referencia: str) -> CheckIn | None:
        """Busca check-in existente para um turno específico."""
        ...

    @abstractmethod
    async def criar(self, checkin: CheckIn) -> CheckIn:
        """Persiste um novo check-in."""
        ...

    @abstractmethod
    async def registrar_duplicata(self, duplicata: CheckInDuplicata) -> CheckInDuplicata:
        """Registra uma tentativa duplicada para auditoria."""
        ...

    @abstractmethod
    async def listar_nao_exportados(self) -> list[CheckIn]:
        """Lista check-ins ainda não exportados para o Google Sheets."""
        ...

    @abstractmethod
    async def marcar_exportado(self, checkin_id: UUID) -> None:
        """Marca um check-in como exportado para o Sheets."""
        ...
