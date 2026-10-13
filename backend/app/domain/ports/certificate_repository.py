from __future__ import annotations

"""Interface de repositório de atestados médicos."""

from abc import ABC, abstractmethod
from uuid import UUID

from ..enums import CertificateStatus
from ..models import CertificateDay, MedicalCertificate


class CertificateRepository(ABC):
    """Port para persistência de atestados médicos e seus vínculos de dias justificados."""

    @abstractmethod
    async def criar(
        self, certificate: MedicalCertificate, dias: list[CertificateDay]
    ) -> MedicalCertificate:
        """Persiste um atestado e seus vínculos de dias justificados."""
        ...

    @abstractmethod
    async def buscar_por_id(self, certificate_id: UUID) -> MedicalCertificate | None:
        """Busca um atestado pelo id (sem os dias)."""
        ...

    @abstractmethod
    async def listar_dias(self, certificate_id: UUID) -> list[CertificateDay]:
        """Lista os dias (turnos) vinculados a um atestado."""
        ...

    @abstractmethod
    async def listar(
        self, user_id: UUID | None = None, status: CertificateStatus | None = None
    ) -> list[MedicalCertificate]:
        """Lista atestados, opcionalmente filtrados por aluno e/ou status."""
        ...

    @abstractmethod
    async def contar_dias_ativos(self, certificate_id: UUID) -> int:
        """Conta os dias ativos vinculados a um atestado."""
        ...

    @abstractmethod
    async def listar_dias_ativos_por_usuario(self, user_id: UUID) -> list[CertificateDay]:
        """Lista todos os dias ativos (de atestados ACTIVE) de um aluno, para a exportação."""
        ...

    @abstractmethod
    async def revogar(
        self, certificate_id: UUID, revogado_por: UUID | None, motivo: str | None
    ) -> MedicalCertificate | None:
        """Revoga um atestado (status REVOKED) e desativa seus dias. Retorna None se inexistente."""
        ...
