from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.adapters.persistence.orm_models import Config as ConfigORM
from app.domain.models import Config
from app.domain.ports.config_repository import ConfigRepository


class ConfigRepositoryImpl(ConfigRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def buscar(self, chave: str) -> str | None:
        stmt = select(ConfigORM).where(ConfigORM.chave == chave)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm:
            return orm.valor

        # Valor padrão caso não exista no banco
        if chave == "CARENCIA_MINUTOS":
            return "10"
        return None

    async def salvar(self, chave: str, valor: str, admin_id: UUID | None = None) -> Config:
        raise NotImplementedError("Configuração ainda não implementada")  # Para uso futuro do dashboard

    async def listar(self) -> list[Config]:
        raise NotImplementedError("Listagem de configurações ainda não implementada")  # Para uso futuro do dashboard
