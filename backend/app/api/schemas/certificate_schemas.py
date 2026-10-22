from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums import CertificateStatus


class JustifiedDay(BaseModel):
    data: date
    turno: str
    turno_referencia: str
    ativo: bool


class CertificateSummary(BaseModel):
    id: UUID
    user_id: UUID
    user_nome: str | None = None
    periodo_inicio: date
    periodo_fim: date
    status: CertificateStatus
    dias_justificados: int
    documento_filename: str
    documento_content_type: str
    criado_em: datetime


class CertificateDetail(CertificateSummary):
    observacao: str | None = None
    registrado_por: UUID | None = None
    revogado_por: UUID | None = None
    revogado_em: datetime | None = None
    motivo_revogacao: str | None = None
    dias: list[JustifiedDay] = []


class RevokeRequest(BaseModel):
    motivo: str | None = None
