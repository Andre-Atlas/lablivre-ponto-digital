from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from uuid import UUID

from app.domain.ports.config_repository import ConfigRepository
from app.domain.models import Config
from app.adapters.persistence.orm_models import Config as ConfigORM


class ConfigRepositoryImpl(ConfigRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def buscar(self, chave: str) -> Optional[str]:
        stmt = select(ConfigORM).where(ConfigORM.chave == chave)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm:
            return orm.valor

        # Valor padrão caso não exista no banco
        if chave == "CARENCIA_MINUTOS":
            return "10"
        return None

    async def salvar(self, chave: str, valor: str, admin_id: Optional[UUID] = None) -> Config:
        pass  # Para uso futuro do dashboard

    async def listar(self) -> List[Config]:
        pass  # Para uso futuro do dashboard
