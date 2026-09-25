from uuid import UUID
from typing import List

from app.domain.ports.user_repository import UserRepository
from app.domain.ports.device_repository import DeviceRepository
from app.domain.ports.checkin_repository import CheckInRepository
from app.domain.models import User, Device, CheckIn

class AdminUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        device_repo: DeviceRepository,
        checkin_repo: CheckInRepository
    ):
        self.user_repo = user_repo
        self.device_repo = device_repo
        self.checkin_repo = checkin_repo

    async def listar_usuarios(self) -> List[User]:
        return await self.user_repo.listar()

    async def aprovar_usuario(self, user_id: UUID) -> User:
        user = await self.user_repo.buscar_por_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        user.admin_aprovado = True
        return await self.user_repo.atualizar(user)

    async def desativar_usuario(self, user_id: UUID) -> User:
        user = await self.user_repo.buscar_por_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        user.ativo = False
        return await self.user_repo.atualizar(user)

    async def listar_dispositivos(self, user_id: UUID) -> List[Device]:
        return await self.device_repo.buscar_por_user(user_id)

    async def listar_checkins_pendentes(self) -> List[CheckIn]:
        return await self.checkin_repo.listar_nao_exportados()
