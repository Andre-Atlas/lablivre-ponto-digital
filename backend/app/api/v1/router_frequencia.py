"""Lançamento de frequência pelo mentor (substitui a autofrequência)."""
from __future__ import annotations

import io
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.database import get_db
from app.adapters.persistence.frequencia_repo_impl import (
    FrequenciaNotFoundError,
    FrequenciaRepositoryImpl,
    FrequenciaValidationError,
)
from app.adapters.persistence.orm_models import User as UserModel
from app.api.schemas.frequencia_schemas import AlunoFrequenciaOut, LancamentoIn
from app.api.v1.router_evaluations import require_mentor
from app.application.frequencia_use_case import FrequenciaUseCase
from app.config import Settings, get_settings
from app.domain.enums import StatusAluno, TipoUsuario

router = APIRouter(prefix="/frequencia", tags=["Frequência"])


def _use_case(db: AsyncSession) -> FrequenciaUseCase:
    return FrequenciaUseCase(FrequenciaRepositoryImpl(db))


@router.get("", response_model=list[AlunoFrequenciaOut])
async def listar_frequencia(
    turma: str = Query(...),
    data: date = Query(...),
    turno: str = Query(...),
    db: AsyncSession = Depends(get_db),
    mentor: UserModel = Depends(require_mentor),
) -> Any:
    """Lista os alunos ATIVOS da turma com o lançamento atual (status + atestado)."""
    alunos = (
        await db.execute(
            select(UserModel).where(
                UserModel.tipo == TipoUsuario.ALUNO,
                UserModel.turma_ou_equipe == turma,
                UserModel.status == StatusAluno.ATIVO,
            )
        )
    ).scalars().all()

    freqs = await FrequenciaRepositoryImpl(db).listar(turma, data, turno)
    by_aluno = {f.aluno_id: f for f in freqs}

    out: list[AlunoFrequenciaOut] = []
    for a in sorted(alunos, key=lambda u: u.nome.lower()):
        f = by_aluno.get(a.id)
        out.append(
            AlunoFrequenciaOut(
                aluno_id=a.id,
                aluno_nome=a.nome,
                freq_id=f.id if f else None,
                status=f.status if f else None,
                tem_atestado=bool(f and f.atestado_documento),
            )
        )
    return out


@router.post("", status_code=200)
async def lancar_frequencia(
    payload: LancamentoIn,
    db: AsyncSession = Depends(get_db),
    mentor: UserModel = Depends(require_mentor),
) -> Any:
    try:
        itens = [(i.aluno_id, i.status) for i in payload.lancamentos]
        await _use_case(db).lancar(mentor.id, payload.turma, payload.data, payload.turno, itens)
        await db.commit()
    except FrequenciaValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    return {"ok": True, "total": len(payload.lancamentos)}


@router.post("/{freq_id}/atestado", status_code=200)
async def anexar_atestado(
    freq_id: UUID,
    documento: UploadFile = File(...),
    observacao: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    mentor: UserModel = Depends(require_mentor),
    settings: Settings = Depends(get_settings),
) -> Any:
    conteudo = await documento.read()
    if len(conteudo) > settings.MAX_CERTIFICATE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Documento excede o tamanho máximo.")
    if documento.content_type not in settings.ALLOWED_CERTIFICATE_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de documento não permitido.")
    try:
        await _use_case(db).anexar_atestado(
            freq_id, conteudo, documento.filename or "atestado", documento.content_type or ""
        )
        await db.commit()
    except FrequenciaNotFoundError:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado.") from None
    except FrequenciaValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    return {"ok": True, "status": "JUSTIFICADO"}


@router.get("/{freq_id}/atestado")
async def baixar_atestado(
    freq_id: UUID,
    db: AsyncSession = Depends(get_db),
    mentor: UserModel = Depends(require_mentor),
) -> Any:
    row = await FrequenciaRepositoryImpl(db).obter(freq_id)
    if row is None or not row.atestado_documento:
        raise HTTPException(status_code=404, detail="Atestado não encontrado.")
    return StreamingResponse(
        io.BytesIO(row.atestado_documento),
        media_type=row.atestado_content_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{row.atestado_filename or "atestado"}"'},
    )


@router.delete("/{freq_id}/atestado", status_code=200)
async def remover_atestado(
    freq_id: UUID,
    db: AsyncSession = Depends(get_db),
    mentor: UserModel = Depends(require_mentor),
) -> Any:
    try:
        await _use_case(db).remover_atestado(freq_id)
        await db.commit()
    except FrequenciaNotFoundError:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado.") from None
    return {"ok": True, "status": "FALTA"}
