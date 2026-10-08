from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from uuid import UUID

from app.domain.ports.checkin_repository import CheckInRepository
from app.domain.models import CheckIn, CheckInDuplicata
from app.domain.enums import StatusCheckin
from app.adapters.persistence.orm_models import (
    Checkin as CheckinORM,
    CheckinDuplicata as DuplicataORM,
)


class CheckInRepositoryImpl(CheckInRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def buscar_por_turno(self, user_id: UUID, turno_referencia: str) -> Optional[CheckIn]:
        stmt = select(CheckinORM).where(
            CheckinORM.user_id == user_id, CheckinORM.turno_referencia == turno_referencia
        )
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if not orm:
            return None
        return self._to_domain(orm)

    async def criar(self, checkin: CheckIn) -> CheckIn:
        orm = CheckinORM(
            id=checkin.id,
            user_id=checkin.user_id,
            device_id=checkin.device_id,
            hora_checkin=checkin.hora_checkin,
            ip_publico=checkin.ip_publico,
            ssid=checkin.ssid,
            bssids=checkin.bssids,
            status=checkin.status,
            turno_referencia=checkin.turno_referencia,
            exportado_sheets=checkin.exportado_sheets,
            criado_em=checkin.criado_em,
        )
        self.session.add(orm)
        await self.session.flush()
        return checkin

    async def registrar_duplicata(self, duplicata: CheckInDuplicata) -> CheckInDuplicata:
        orm = DuplicataORM(
            id=duplicata.id,
            checkin_original_id=duplicata.checkin_original_id,
            user_id=duplicata.user_id,
            device_id=duplicata.device_id,
            hora_tentativa=duplicata.hora_tentativa,
            ip_publico=duplicata.ip_publico,
            motivo=duplicata.motivo,
            criado_em=duplicata.criado_em,
        )
        self.session.add(orm)
        await self.session.flush()
        return duplicata

    async def listar_nao_exportados(self) -> List[CheckIn]:
        stmt = select(CheckinORM).where(CheckinORM.exportado_sheets == False)
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def marcar_exportado(self, checkin_id: UUID) -> None:
        stmt = select(CheckinORM).where(CheckinORM.id == checkin_id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm:
            orm.exportado_sheets = True
            await self.session.flush()

    def _to_domain(self, orm: CheckinORM) -> CheckIn:
        return CheckIn(
            id=orm.id,
            user_id=orm.user_id,
            device_id=orm.device_id,
            hora_checkin=orm.hora_checkin,
            ip_publico=orm.ip_publico,
            ssid=orm.ssid,
            bssids=orm.bssids,
            status=StatusCheckin(orm.status),
            turno_referencia=orm.turno_referencia,
            exportado_sheets=orm.exportado_sheets,
            criado_em=orm.criado_em,
        )
