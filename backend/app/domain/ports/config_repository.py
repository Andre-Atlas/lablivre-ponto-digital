from __future__ import annotations

"""Interface de repositório de configurações dinâmicas."""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models import Config


class ConfigRepository(ABC):
    """Port para persistência de configurações chave-valor."""

    @abstractmethod
    async def buscar(self, chave: str) -> str | None:
        """Busca o valor de uma configuração pela chave."""
        ...

    @abstractmethod
    async def salvar(self, chave: str, valor: str, admin_id: UUID | None = None) -> Config:
        """Salva ou atualiza uma configuração."""
        ...

    @abstractmethod
    async def listar(self) -> list[Config]:
        """Lista todas as configurações."""
        ...
