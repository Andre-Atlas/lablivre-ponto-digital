from __future__ import annotations

import io
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.certificate_repo_impl import (
    CertificateAlreadyRevokedError,
    CertificateRepositoryImpl,
)
from app.adapters.persistence.checkin_repo_impl import CheckInRepositoryImpl
from app.adapters.persistence.database import get_db
from app.adapters.persistence.orm_models import User as UserModel
from app.api.schemas.certificate_schemas import (
    CertificateDetail,
    CertificateSummary,
    JustifiedDay,
    RevokeRequest,
)
from app.api.v1.router_admin import require_admin
from app.application.certificate_use_case import (
    CertificateNotFoundError,
    CertificateUseCase,
    CertificateValidationError,
)
from app.config import Settings, get_settings
from app.domain.enums import CertificateStatus
from app.domain.models import CertificateDay, MedicalCertificate

router = APIRouter(prefix="/admin/certificados", tags=["Atestados Médicos"])


def _use_case(db: AsyncSession) -> CertificateUseCase:
    return CertificateUseCase(CertificateRepositoryImpl(db), CheckInRepositoryImpl(db))


def _to_detail(
    cert: MedicalCertificate, dias: list[CertificateDay], user_nome: str | None
) -> CertificateDetail:
    ativos = sum(1 for d in dias if d.ativo)
    return CertificateDetail(
        id=cert.id,
        user_id=cert.user_id,
        user_nome=user_nome,
        periodo_inicio=cert.periodo_inicio,
        periodo_fim=cert.periodo_fim,
        status=cert.status,
        dias_justificados=ativos,
        documento_filename=cert.documento_filename,
        documento_content_type=cert.documento_content_type,
        criado_em=cert.criado_em,
        observacao=cert.observacao,
        registrado_por=cert.registrado_por,
        revogado_por=cert.revogado_por,
        revogado_em=cert.revogado_em,
        motivo_revogacao=cert.motivo_revogacao,
        dias=[
            JustifiedDay(
                data=d.data, turno=d.turno, turno_referencia=d.turno_referencia, ativo=d.ativo
            )
            for d in dias
        ],
    )


@router.post(
    "",
    status_code=201,
    response_model=CertificateDetail,
    summary="Registra um atestado médico para um aluno (justifica faltas cobertas ao salvar)",
)
async def registrar_atestado(
    user_id: UUID = Form(...),
    periodo_inicio: date = Form(...),
    periodo_fim: date = Form(...),
    observacao: str | None = Form(None),
    documento: UploadFile = File(...),
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    aluno = (await db.execute(select(UserModel).where(UserModel.id == user_id))).scalars().first()
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    conteudo = await documento.read()
    try:
        cert, dias = await _use_case(db).registrar(
            user_id=user_id,
            tipo=aluno.tipo,
            turma_ou_equipe=aluno.turma_ou_equipe,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            documento=conteudo,
            documento_filename=documento.filename or "atestado",
            documento_content_type=documento.content_type or "application/octet-stream",
            observacao=observacao,
            registrado_por=current_admin.id,
            allowed_content_types=settings.ALLOWED_CERTIFICATE_CONTENT_TYPES,
            max_size_bytes=settings.MAX_CERTIFICATE_SIZE_BYTES,
        )
    except CertificateValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_detail(cert, dias, aluno.nome)


@router.get(
    "",
    response_model=list[CertificateSummary],
    summary="Lista atestados (filtra por aluno e/ou status)",
)
async def listar_atestados(
    user_id: UUID | None = None,
    status: CertificateStatus | None = None,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    resultado = await _use_case(db).listar(user_id=user_id, status=status)
    # Resolve nomes dos alunos em lote
    ids = {cert.user_id for cert, _ in resultado}
    nomes: dict[UUID, str] = {}
    if ids:
        rows = (
            await db.execute(select(UserModel.id, UserModel.nome).where(UserModel.id.in_(ids)))
        ).all()
        nomes = {r[0]: r[1] for r in rows}
    return [
        CertificateSummary(
            id=cert.id,
            user_id=cert.user_id,
            user_nome=nomes.get(cert.user_id),
            periodo_inicio=cert.periodo_inicio,
            periodo_fim=cert.periodo_fim,
            status=cert.status,
            dias_justificados=ativos,
            documento_filename=cert.documento_filename,
            documento_content_type=cert.documento_content_type,
            criado_em=cert.criado_em,
        )
        for cert, ativos in resultado
    ]


@router.get(
    "/{certificate_id}",
    response_model=CertificateDetail,
    summary="Obtém um atestado com os dias que ele justificou",
)
async def obter_atestado(
    certificate_id: UUID,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    try:
        cert, dias = await _use_case(db).obter(certificate_id)
    except CertificateNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Atestado não encontrado") from exc
    aluno = (
        (await db.execute(select(UserModel.nome).where(UserModel.id == cert.user_id)))
        .scalars()
        .first()
    )
    return _to_detail(cert, dias, aluno)


@router.get(
    "/{certificate_id}/documento",
    summary="Baixa o documento do atestado (apenas admin; dado sensível de saúde)",
)
async def baixar_documento(
    certificate_id: UUID,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    cert = await CertificateRepositoryImpl(db).buscar_por_id(certificate_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Atestado não encontrado")
    return StreamingResponse(
        io.BytesIO(cert.documento),
        media_type=cert.documento_content_type,
        headers={
            "Content-Disposition": f'inline; filename="{cert.documento_filename}"',
        },
    )


@router.post(
    "/{certificate_id}/revogar",
    response_model=CertificateDetail,
    summary="Revoga um atestado (reverte os dias justificados exclusivamente por ele)",
)
async def revogar_atestado(
    certificate_id: UUID,
    request: RevokeRequest | None = None,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    motivo = request.motivo if request else None
    try:
        await _use_case(db).revogar(certificate_id, current_admin.id, motivo)
    except CertificateAlreadyRevokedError as exc:
        raise HTTPException(status_code=409, detail="Atestado já revogado") from exc
    except CertificateNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Atestado não encontrado") from exc
    cert, dias = await _use_case(db).obter(certificate_id)
    aluno = (
        (await db.execute(select(UserModel.nome).where(UserModel.id == cert.user_id)))
        .scalars()
        .first()
    )
    return _to_detail(cert, dias, aluno)
