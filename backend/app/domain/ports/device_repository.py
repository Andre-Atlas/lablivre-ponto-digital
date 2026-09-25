from __future__ import annotations

"""Interface de repositório de dispositivos."""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models import Device


class DeviceRepository(ABC):
    """Port para persistência de dispositivos."""

    @abstractmethod
    async def buscar_por_mac(self, mac_address: str) -> Device | None:
        """Busca um dispositivo pelo MAC address."""
        ...

    @abstractmethod
    async def buscar_por_user(self, user_id: UUID) -> list[Device]:
        """Lista todos os dispositivos de um usuário."""
        ...

    @abstractmethod
    async def criar(self, device: Device) -> Device:
        """Registra um novo dispositivo."""
        ...
