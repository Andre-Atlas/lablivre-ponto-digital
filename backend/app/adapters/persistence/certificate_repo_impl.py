from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.orm_models import (
    CertificateDay as CertificateDayORM,
)
from app.adapters.persistence.orm_models import (
    MedicalCertificate as MedicalCertificateORM,
)
from app.domain.enums import CertificateStatus
from app.domain.models import CertificateDay, MedicalCertificate
from app.domain.ports.certificate_repository import CertificateRepository


class CertificateRepositoryImpl(CertificateRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def criar(
        self, certificate: MedicalCertificate, dias: list[CertificateDay]
    ) -> MedicalCertificate:
        orm = MedicalCertificateORM(
            id=certificate.id,
            user_id=certificate.user_id,
            periodo_inicio=certificate.periodo_inicio,
            periodo_fim=certificate.periodo_fim,
            documento=certificate.documento,
            documento_filename=certificate.documento_filename,
            documento_content_type=certificate.documento_content_type,
            documento_tamanho=certificate.documento_tamanho,
            observacao=certificate.observacao,
            status=certificate.status,
            registrado_por=certificate.registrado_por,
            criado_em=certificate.criado_em,
        )
        self.session.add(orm)
        for dia in dias:
            self.session.add(
                CertificateDayORM(
                    id=dia.id,
                    certificate_id=certificate.id,
                    user_id=dia.user_id,
                    data=dia.data,
                    turno=dia.turno,
                    turno_referencia=dia.turno_referencia,
                    ativo=dia.ativo,
                    criado_em=dia.criado_em,
                )
            )
        await self.session.commit()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def buscar_por_id(self, certificate_id: UUID) -> MedicalCertificate | None:
        stmt = select(MedicalCertificateORM).where(MedicalCertificateORM.id == certificate_id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        return self._to_domain(orm) if orm else None

    async def listar_dias(self, certificate_id: UUID) -> list[CertificateDay]:
        stmt = (
            select(CertificateDayORM)
            .where(CertificateDayORM.certificate_id == certificate_id)
            .order_by(CertificateDayORM.data, CertificateDayORM.turno)
        )
        result = await self.session.execute(stmt)
        return [self._day_to_domain(orm) for orm in result.scalars().all()]

    async def listar(
        self, user_id: UUID | None = None, status: CertificateStatus | None = None
    ) -> list[MedicalCertificate]:
        stmt = select(MedicalCertificateORM)
        if user_id is not None:
            stmt = stmt.where(MedicalCertificateORM.user_id == user_id)
        if status is not None:
            stmt = stmt.where(MedicalCertificateORM.status == status)
        stmt = stmt.order_by(MedicalCertificateORM.criado_em.desc())
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def contar_dias_ativos(self, certificate_id: UUID) -> int:
        stmt = select(func.count()).where(
            CertificateDayORM.certificate_id == certificate_id,
            CertificateDayORM.ativo == True,  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def listar_dias_ativos_por_usuario(self, user_id: UUID) -> list[CertificateDay]:
        stmt = (
            select(CertificateDayORM)
            .join(
                MedicalCertificateORM,
                MedicalCertificateORM.id == CertificateDayORM.certificate_id,
            )
            .where(
                CertificateDayORM.user_id == user_id,
                CertificateDayORM.ativo == True,  # noqa: E712
                MedicalCertificateORM.status == CertificateStatus.ACTIVE,
            )
        )
        result = await self.session.execute(stmt)
        return [self._day_to_domain(orm) for orm in result.scalars().all()]

    async def revogar(
        self, certificate_id: UUID, revogado_por: UUID | None, motivo: str | None
    ) -> MedicalCertificate | None:
        stmt = select(MedicalCertificateORM).where(MedicalCertificateORM.id == certificate_id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if not orm:
            return None
        if orm.status == CertificateStatus.REVOKED:
            # Já revogado — sinaliza com exceção controlada no caso de uso.
            raise CertificateAlreadyRevokedError(certificate_id)

        orm.status = CertificateStatus.REVOKED
        orm.revogado_por = revogado_por
        orm.motivo_revogacao = motivo
        orm.revogado_em = datetime.now(UTC)
        await self.session.execute(
            update(CertificateDayORM)
            .where(CertificateDayORM.certificate_id == certificate_id)
            .values(ativo=False)
        )
        await self.session.commit()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    def _to_domain(self, orm: MedicalCertificateORM) -> MedicalCertificate:
        return MedicalCertificate(
            id=orm.id,
            user_id=orm.user_id,
            periodo_inicio=orm.periodo_inicio,
            periodo_fim=orm.periodo_fim,
            documento=bytes(orm.documento),
            documento_filename=orm.documento_filename,
            documento_content_type=orm.documento_content_type,
            documento_tamanho=orm.documento_tamanho,
            status=CertificateStatus(orm.status),
            criado_em=orm.criado_em,
            observacao=orm.observacao,
            registrado_por=orm.registrado_por,
            revogado_por=orm.revogado_por,
            motivo_revogacao=orm.motivo_revogacao,
            revogado_em=orm.revogado_em,
        )

    def _day_to_domain(self, orm: CertificateDayORM) -> CertificateDay:
        return CertificateDay(
            id=orm.id,
            certificate_id=orm.certificate_id,
            user_id=orm.user_id,
            data=orm.data,
            turno=orm.turno,
            turno_referencia=orm.turno_referencia,
            ativo=orm.ativo,
            criado_em=orm.criado_em,
        )


class CertificateAlreadyRevokedError(Exception):
    """Levantada ao tentar revogar um atestado já revogado."""

    def __init__(self, certificate_id: UUID) -> None:
        self.certificate_id = certificate_id
        super().__init__(f"Atestado {certificate_id} já está revogado.")
