"""Interface do serviço de exportação para Google Sheets."""

from abc import ABC, abstractmethod

from ..models import CheckIn, User, Device


class SheetsService(ABC):
    """Port para exportação de check-ins para planilhas Google."""

    @abstractmethod
    async def exportar_checkin_aluno(self, checkin: CheckIn, user: User, device: Device) -> bool:
        """Exporta check-in de aluno para a planilha de alunos."""
        ...

    @abstractmethod
    async def exportar_checkin_staff(self, checkin: CheckIn, user: User, device: Device) -> bool:
        """Exporta check-in de staff para a planilha de staff."""
        ...
