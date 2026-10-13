from __future__ import annotations

"""Caso de uso de atestados médicos.

Orquestra o registro, consulta e revogação de atestados e a materialização dos vínculos
de dias justificados (CertificateDay), isolando a regra de negócio do transporte (FastAPI)
e da persistência (SQLAlchemy).
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime
from uuid import UUID

from app.domain.enums import CertificateStatus, StatusCheckin, TipoUsuario
from app.domain.models import (
    CertificateDay,
    MedicalCertificate,
    expandir_turnos_periodo,
    periodo_valido,
)
from app.domain.ports.certificate_repository import CertificateRepository
from app.domain.ports.checkin_repository import CheckInRepository

# Status de check-in que representam presença real e, portanto, NÃO são justificáveis.
_PRESENCA_REAL = {StatusCheckin.PRESENTE, StatusCheckin.ATRASADO}


class CertificateValidationError(Exception):
    """Erro de validação de atestado (período, documento, tipo de usuário)."""


class CertificateNotFoundError(Exception):
    """Atestado não encontrado."""


class CertificateUseCase:
    def __init__(self, cert_repo: CertificateRepository, checkin_repo: CheckInRepository) -> None:
        self.cert_repo = cert_repo
        self.checkin_repo = checkin_repo

    async def registrar(
        self,
        *,
        user_id: UUID,
        tipo: TipoUsuario,
        turma_ou_equipe: str,
        periodo_inicio: date,
        periodo_fim: date,
        documento: bytes,
        documento_filename: str,
        documento_content_type: str,
        observacao: str | None,
        registrado_por: UUID | None,
        allowed_content_types: Sequence[str],
        max_size_bytes: int,
    ) -> tuple[MedicalCertificate, list[CertificateDay]]:
        # Validações (FR-003, FR-005a, FR-017)
        if tipo != TipoUsuario.ALUNO:
            raise CertificateValidationError(
                "Atestados só podem ser registrados para alunos (ALUNO)."
            )
        if not documento:
            raise CertificateValidationError("Documento do atestado é obrigatório.")
        if documento_content_type not in allowed_content_types:
            raise CertificateValidationError(
                "Tipo de documento não suportado. Use PDF, JPEG ou PNG."
            )
        tamanho = len(documento)
        if tamanho > max_size_bytes:
            raise CertificateValidationError("Documento excede o tamanho máximo de 10 MB.")
        if not periodo_valido(periodo_inicio, periodo_fim):
            raise CertificateValidationError(
                "Data final do período não pode ser anterior à inicial."
            )

        cert_id = uuid.uuid4()
        agora = datetime.now(UTC)
        certificate = MedicalCertificate(
            id=cert_id,
            user_id=user_id,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            documento=documento,
            documento_filename=documento_filename,
            documento_content_type=documento_content_type,
            documento_tamanho=tamanho,
            status=CertificateStatus.ACTIVE,
            criado_em=agora,
            observacao=observacao,
            registrado_por=registrado_por,
        )

        # FR-006: vincula os turnos esperados no período SEM check-in presente/atrasado real
        # (ou seja, FALTA ou já JUSTIFICADO). Turnos com presença real são excluídos.
        dias: list[CertificateDay] = []
        for data_turno, turno, turno_ref in expandir_turnos_periodo(
            turma_ou_equipe, periodo_inicio, periodo_fim
        ):
            checkin = await self.checkin_repo.buscar_por_turno(user_id, turno_ref)
            if checkin is not None and checkin.status in _PRESENCA_REAL:
                continue  # presença real — não justificar
            dias.append(
                CertificateDay(
                    id=uuid.uuid4(),
                    certificate_id=cert_id,
                    user_id=user_id,
                    data=data_turno,
                    turno=turno.value,
                    turno_referencia=turno_ref,
                    ativo=True,
                    criado_em=agora,
                )
            )

        persisted = await self.cert_repo.criar(certificate, dias)
        return persisted, dias

    async def obter(self, certificate_id: UUID) -> tuple[MedicalCertificate, list[CertificateDay]]:
        certificate = await self.cert_repo.buscar_por_id(certificate_id)
        if certificate is None:
            raise CertificateNotFoundError(str(certificate_id))
        dias = await self.cert_repo.listar_dias(certificate_id)
        return certificate, dias

    async def listar(
        self, user_id: UUID | None = None, status: CertificateStatus | None = None
    ) -> list[tuple[MedicalCertificate, int]]:
        certificados = await self.cert_repo.listar(user_id=user_id, status=status)
        resultado: list[tuple[MedicalCertificate, int]] = []
        for cert in certificados:
            ativos = await self.cert_repo.contar_dias_ativos(cert.id)
            resultado.append((cert, ativos))
        return resultado

    async def revogar(
        self, certificate_id: UUID, revogado_por: UUID | None, motivo: str | None
    ) -> MedicalCertificate:
        certificate = await self.cert_repo.revogar(certificate_id, revogado_por, motivo)
        if certificate is None:
            raise CertificateNotFoundError(str(certificate_id))
        return certificate
