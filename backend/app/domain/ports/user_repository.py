from __future__ import annotations

"""Interface de repositório de usuários."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..enums import TipoUsuario
from ..models import User


class UserRepository(ABC):
    """Port para persistência de usuários."""

    @abstractmethod
    async def buscar_por_id(self, user_id: UUID) -> User | None:
        """Busca um usuário pelo ID."""
        ...

    @abstractmethod
    async def buscar_por_email(self, email: str) -> User | None:
        """Busca um usuário pelo e-mail."""
        ...

    @abstractmethod
    async def criar(self, user: User) -> User:
        """Persiste um novo usuário."""
        ...

    @abstractmethod
    async def atualizar(self, user: User) -> User:
        """Atualiza os dados de um usuário existente."""
        ...

    @abstractmethod
    async def listar(
        self,
        tipo: TipoUsuario | None = None,
        turma: str | None = None,
    ) -> list[User]:
        """Lista usuários com filtros opcionais."""
        ...
