from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from uuid import UUID

from app.domain.ports.device_repository import DeviceRepository
from app.domain.models import Device
from app.adapters.persistence.orm_models import Device as DeviceORM

class DeviceRepositoryImpl(DeviceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def buscar_por_mac(self, mac_address: str) -> Optional[Device]:
        stmt = select(DeviceORM).where(DeviceORM.mac_address == mac_address)
        result = await self.session.execute(stmt)
        device_orm = result.scalars().first()
        if not device_orm: return None
        return self._to_domain(device_orm)

    async def buscar_por_user(self, user_id: UUID) -> List[Device]:
        stmt = select(DeviceORM).where(DeviceORM.user_id == user_id)
        result = await self.session.execute(stmt)
        return [self._to_domain(d) for d in result.scalars().all()]

    async def criar(self, device: Device) -> Device:
        device_orm = DeviceORM(
            id=device.id,
            user_id=device.user_id,
            mac_address=device.mac_address,
            os_type=device.os_type,
            hostname=device.hostname,
            serial_number=device.serial_number,
            principal=device.principal,
            registrado_em=device.registrado_em
        )
        self.session.add(device_orm)
        await self.session.flush()
        return device

    def _to_domain(self, device_orm: DeviceORM) -> Device:
        return Device(
            id=device_orm.id,
            user_id=device_orm.user_id,
            mac_address=device_orm.mac_address,
            os_type=device_orm.os_type,
            hostname=device_orm.hostname,
            serial_number=device_orm.serial_number,
            principal=device_orm.principal,
            registrado_em=device_orm.registrado_em
        )
