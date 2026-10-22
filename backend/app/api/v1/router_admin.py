from __future__ import annotations

import calendar
import csv
import io
import json
import uuid
from datetime import UTC, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import openpyxl
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.database import get_db
from app.adapters.persistence.orm_models import Checkin as CheckInModel
from app.adapters.persistence.orm_models import Config as ConfigModel
from app.adapters.persistence.orm_models import Device as DeviceModel
from app.adapters.persistence.orm_models import Frequencia as FrequenciaModel
from app.adapters.persistence.orm_models import MentorTurma as MentorTurmaModel
from app.adapters.persistence.orm_models import User as UserModel
from app.api.middleware.auth_dependencies import get_current_user
from app.domain.enums import (
    CertificateStatus,
    RoleAdmin,
    StatusAluno,
    StatusCheckin,
    TipoUsuario,
)
from app.domain.models import User
from app.utils.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Administração"])


class UserAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    email: str
    tipo: TipoUsuario
    role: RoleAdmin | None = None
    admin_aprovado: bool
    status: StatusAluno = StatusAluno.ATIVO


async def require_admin(
    payload: dict[str, Any] = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token inválido") from None
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido") from None

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    current_user = result.scalars().first()

    if not current_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if current_user.role not in [RoleAdmin.SUPER_ADMIN, RoleAdmin.ADMIN]:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
    return current_user


@router.get("/usuarios", response_model=list[UserAdminResponse])
async def list_usuarios(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> Any:
    stmt = select(UserModel)
    if status:
        stmt = stmt.where(UserModel.status == status)
    users = (await db.execute(stmt)).scalars().all()
    return users  # from_attributes=True no schema cuida da serialização.


@router.post("/usuarios/{user_id}/aprovar")
async def aprovar_usuario(
    user_id: UUID, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)
) -> Any:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user_model = result.scalars().first()

    if not user_model:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    user_model.admin_aprovado = True
    await db.commit()
    return {"message": f"Usuário {user_model.nome} aprovado com sucesso."}


class CreateAdminRequest(BaseModel):
    nome: str
    email: str
    senha: str
    role: str = "STAFF"


@router.post("/usuarios")
async def create_admin(
    request: CreateAdminRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, Any]:
    # Verify email uniqueness
    existing = await db.execute(select(UserModel).where(UserModel.email == request.email))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    new_admin = UserModel(
        email=request.email,
        nome=request.nome,
        tipo=TipoUsuario.STAFF,
        role=RoleAdmin(request.role.upper()) if request.role else RoleAdmin.NONE,
        turma_ou_equipe="Administração",
        oauth_provider="manual",
        oauth_sub=f"manual_{uuid.uuid4()}",
        admin_aprovado=True,
        senha_hash=get_password_hash(request.senha),
    )
    db.add(new_admin)
    await db.commit()
    return {"message": f"Administrador {new_admin.nome} criado com sucesso."}


# ─────────────────────────── Turmas (cadastro) ───────────────────────────

TURMAS_CONFIG_KEY = "turmas"


async def _get_turmas(db: AsyncSession) -> list[str]:
    """Lista de turmas cadastradas (armazenadas como JSON na tabela config)."""
    res = await db.execute(select(ConfigModel).where(ConfigModel.chave == TURMAS_CONFIG_KEY))
    row = res.scalars().first()
    if not row or not row.valor:
        return []
    try:
        data = json.loads(row.valor)
    except (ValueError, TypeError):
        return []
    return [str(t) for t in data] if isinstance(data, list) else []


async def _set_turmas(db: AsyncSession, turmas: list[str]) -> None:
    res = await db.execute(select(ConfigModel).where(ConfigModel.chave == TURMAS_CONFIG_KEY))
    row = res.scalars().first()
    now = datetime.now(UTC)
    valor = json.dumps(turmas, ensure_ascii=False)
    if row:
        row.valor = valor
        row.atualizado_em = now
    else:
        db.add(ConfigModel(chave=TURMAS_CONFIG_KEY, valor=valor, atualizado_em=now))
    await db.commit()


@router.get("/turmas")
async def list_turmas(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[str]:
    return sorted(await _get_turmas(db))


class TurmaRequest(BaseModel):
    nome: str


@router.post("/turmas", status_code=201)
async def create_turma(
    request: TurmaRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[str]:
    nome = request.nome.strip()
    if not nome:
        raise HTTPException(status_code=400, detail="Nome da turma é obrigatório.")
    turmas = await _get_turmas(db)
    if any(t.lower() == nome.lower() for t in turmas):
        raise HTTPException(status_code=409, detail="Turma já cadastrada.")
    turmas.append(nome)
    await _set_turmas(db, turmas)
    return sorted(turmas)


@router.delete("/turmas/{nome}")
async def delete_turma(
    nome: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[str]:
    turmas = await _get_turmas(db)
    novas = [t for t in turmas if t.lower() != nome.strip().lower()]
    if len(novas) == len(turmas):
        raise HTTPException(status_code=404, detail="Turma não encontrada.")
    await _set_turmas(db, novas)
    return sorted(novas)


# ─────────────────────────── Vínculo mentor–turma ───────────────────────────


class MentorTurmasRequest(BaseModel):
    turmas: list[str]


@router.get("/mentores/{user_id}/turmas", response_model=list[str])
async def get_mentor_turmas(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> Any:
    rows = await db.execute(
        select(MentorTurmaModel.turma).where(MentorTurmaModel.user_id == user_id)
    )
    return sorted(r[0] for r in rows.all())


@router.put("/mentores/{user_id}/turmas", response_model=list[str])
async def set_mentor_turmas(
    user_id: UUID,
    request: MentorTurmasRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> Any:
    mentor = (await db.execute(select(UserModel).where(UserModel.id == user_id))).scalars().first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor não encontrado.")
    if mentor.tipo != TipoUsuario.STAFF and mentor.role not in (RoleAdmin.ADMIN, RoleAdmin.SUPER_ADMIN):
        raise HTTPException(status_code=400, detail="Só mentores (staff/admin) podem ser atrelados a turmas.")

    cadastradas = set(await _get_turmas(db))
    novas = {t.strip() for t in request.turmas if t.strip()}
    invalidas = novas - cadastradas
    if invalidas:
        raise HTTPException(
            status_code=400, detail=f"Turma(s) não cadastrada(s): {', '.join(sorted(invalidas))}"
        )

    await db.execute(MentorTurmaModel.__table__.delete().where(MentorTurmaModel.user_id == user_id))
    now = datetime.now(UTC)
    for t in sorted(novas):
        db.add(MentorTurmaModel(id=uuid.uuid4(), user_id=user_id, turma=t, criado_em=now))
    await db.commit()
    return sorted(novas)


class CreateAlunoRequest(BaseModel):
    nome: str
    email: str
    turma_ou_equipe: str


@router.post("/alunos", status_code=201)
async def create_aluno(
    request: CreateAlunoRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, Any]:
    """Registra um aluno (ALUNO) como registro administrado — sem senha/login próprio."""
    if not request.nome.strip() or not request.email.strip():
        raise HTTPException(status_code=400, detail="Nome e e-mail são obrigatórios.")
    if not request.turma_ou_equipe.strip():
        raise HTTPException(status_code=400, detail="Turma é obrigatória.")
    turmas = await _get_turmas(db)
    if request.turma_ou_equipe.strip() not in turmas:
        raise HTTPException(
            status_code=400, detail="Turma não cadastrada. Cadastre a turma antes de registrar o aluno."
        )
    existing = await db.execute(select(UserModel).where(UserModel.email == request.email))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    aluno = UserModel(
        email=request.email,
        nome=request.nome.strip(),
        tipo=TipoUsuario.ALUNO,
        role=RoleAdmin.NONE,
        turma_ou_equipe=request.turma_ou_equipe.strip(),
        oauth_provider="manual",
        oauth_sub=f"manual_{uuid.uuid4()}",
        admin_aprovado=True,
    )
    db.add(aluno)
    await db.commit()
    await db.refresh(aluno)
    return {"id": str(aluno.id), "nome": aluno.nome, "tipo": aluno.tipo.value}


class StatusAlunoRequest(BaseModel):
    status: str


@router.put("/alunos/{user_id}/status", response_model=UserAdminResponse)
async def set_aluno_status(
    user_id: UUID,
    request: StatusAlunoRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> Any:
    aluno = (await db.execute(select(UserModel).where(UserModel.id == user_id))).scalars().first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    try:
        aluno.status = StatusAluno(request.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Status inválido (use ATIVO ou DESLIGADO).") from None
    await db.commit()
    await db.refresh(aluno)
    return aluno


@router.delete("/usuarios/{user_id}")
async def delete_usuario(
    user_id: UUID, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)
) -> Any:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user_model = result.scalars().first()

    if not user_model:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if user_model.id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta.")

    await db.delete(user_model)
    await db.commit()
    return {"message": "Usuário excluído com sucesso."}


@router.get("/export/usuarios")
async def export_usuarios(
    db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)
) -> Any:
    result = await db.execute(select(UserModel))
    users = result.scalars().all()

    output_csv = io.StringIO()
    writer = csv.writer(output_csv)
    writer.writerow(["ID", "Nome", "Email", "Tipo", "Status", "Aprovado", "Turma", "Máquina", "Criado Em"])

    for u in users:
        writer.writerow(
            [
                str(u.id),
                u.nome,
                u.email,
                u.tipo.value if u.tipo else "",
                u.status.value if u.status else "",
                "Sim" if u.admin_aprovado else "Nao",
                u.turma_ou_equipe or "",
                u.patrimonio or "",
                u.criado_em.replace(tzinfo=UTC)
                .astimezone(timezone(timedelta(hours=-3)))
                .strftime("%Y-%m-%d %H:%M:%S")
                if u.criado_em
                else "",
            ]
        )

    output_csv.seek(0)
    return StreamingResponse(
        iter([output_csv.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=usuarios_lablivre.csv"},
    )


@router.get("/export/frequencia")
async def export_frequencia(
    turma: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> Any:
    """Relatório de frequência lançada pelos mentores (inclui alunos Desligados, marcados)."""
    stmt = (
        select(FrequenciaModel, UserModel)
        .join(UserModel, FrequenciaModel.aluno_id == UserModel.id)
        .order_by(FrequenciaModel.data, FrequenciaModel.turma, UserModel.nome)
    )
    if turma:
        stmt = stmt.where(FrequenciaModel.turma == turma)
    rows = (await db.execute(stmt)).all()

    output_csv = io.StringIO()
    writer = csv.writer(output_csv)
    writer.writerow(["Data", "Turno", "Turma", "Aluno", "Status Aluno", "Frequência", "Atestado"])
    for freq, u in rows:
        writer.writerow(
            [
                freq.data.isoformat(),
                freq.turno,
                freq.turma,
                u.nome,
                u.status.value if u.status else "",
                freq.status,
                "Sim" if freq.atestado_documento else "Nao",
            ]
        )
    output_csv.seek(0)
    return StreamingResponse(
        iter([output_csv.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=frequencia.csv"},
    )


@router.get("/export/checkins")
async def export_checkins(
    tipo: TipoUsuario | None = None,
    format: str | None = "csv",
    ano: int | None = None,
    mes: int | None = None,
    dia: int | None = None,
    turma: str | None = None,
    turno: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> StreamingResponse:
    query = select(CheckInModel, UserModel).join(UserModel, CheckInModel.user_id == UserModel.id)
    if tipo:
        query = query.where(UserModel.tipo == tipo)
    if turma:
        query = query.where(UserModel.turma_ou_equipe.ilike(f"%{turma}%"))
    if turno:
        query = query.where(CheckInModel.turno_referencia.ilike(f"%{turno}%"))
    if ano is not None and mes is not None and dia is not None:
        # Approximate filter in DB for the specific day (UTC boundaries might slightly shift, but it's okay for general query)
        start_date = datetime(ano, mes, dia, tzinfo=UTC)
        end_date = start_date + timedelta(days=1)
        query = query.where(
            CheckInModel.hora_checkin >= start_date, CheckInModel.hora_checkin < end_date
        )

    now_utc = datetime.now(UTC)
    target_year = ano if ano else now_utc.year
    target_month = mes if mes else now_utc.month

    query = query.order_by(CheckInModel.hora_checkin.desc())
    result = await db.execute(query)
    rows = result.all()

    # ── Dados compartilhados entre as exportações CSV e Excel ───────────────────
    from app.adapters.persistence.orm_models import CertificateDay as _CDay
    from app.adapters.persistence.orm_models import MedicalCertificate as _MCert
    from app.domain.models import _DIA_SEMANA_MAP, TURNOS_ALUNOS

    # Organiza check-ins por usuário
    checkins_by_user: dict[Any, Any] = {}
    for checkin, user in rows:
        checkins_by_user.setdefault(user.id, []).append(checkin)

    # Busca todos os usuários para calcular faltas mesmo de quem não bateu ponto
    all_users = (await db.execute(select(UserModel))).scalars().all()

    # Cobertura de atestados ativos: user_id -> {turno_referencia: certificate_id}
    cover_rows = (
        await db.execute(
            select(_CDay.user_id, _CDay.turno_referencia, _CDay.certificate_id)
            .join(_MCert, _MCert.id == _CDay.certificate_id)
            .where(_CDay.ativo == True, _MCert.status == CertificateStatus.ACTIVE)  # noqa: E712
        )
    ).all()
    cert_cover: dict[Any, dict[str, Any]] = {}
    for uid, ref, cid in cover_rows:
        cert_cover.setdefault(uid, {})[ref] = cid

    num_days = calendar.monthrange(target_year, target_month)[1]
    br = timezone(timedelta(hours=-3))

    def _fmt(dt: datetime | None) -> str:
        return dt.replace(tzinfo=UTC).astimezone(br).strftime("%Y-%m-%d %H:%M:%S") if dt else ""

    def _status_para(found_checkin: Any, user_id: Any, expected_ref: str) -> str:
        # Presença/atraso reais prevalecem; depois atestado; senão FALTA.
        if found_checkin is not None and found_checkin.status in (
            StatusCheckin.PRESENTE,
            StatusCheckin.ATRASADO,
        ):
            return str(found_checkin.status.value)
        cid = cert_cover.get(user_id, {}).get(expected_ref)
        if cid is not None:
            return f"JUSTIFICADO (Atestado {str(cid)[:8]})"
        if found_checkin is not None and found_checkin.status:
            return str(found_checkin.status.value)
        return "FALTA"

    # Linhas de alunos (8 colunas) e de staff (7 colunas), calculadas uma única vez.
    aluno_rows: list[list[str]] = []
    staff_rows: list[list[str]] = []
    for user in all_users:
        if tipo and user.tipo != tipo:
            continue
        user_checkins = checkins_by_user.get(user.id, [])

        if user.tipo == TipoUsuario.STAFF:
            for checkin in user_checkins:
                if (
                    checkin.hora_checkin
                    and checkin.hora_checkin.year == target_year
                    and checkin.hora_checkin.month == target_month
                ):
                    staff_rows.append(
                        [
                            user.nome,
                            user.email,
                            user.patrimonio or "",
                            _fmt(checkin.hora_checkin),
                            checkin.turno_referencia or "",
                            checkin.status.value if checkin.status else "",
                            checkin.ip_publico or "",
                        ]
                    )
            continue

        # ALUNO: enumera turnos esperados e classifica (PRESENTE/ATRASADO/JUSTIFICADO/FALTA)
        if not user.turma_ou_equipe:
            continue
        turma_shifts = [t for t in TURNOS_ALUNOS if t.turma == user.turma_ou_equipe]
        if not turma_shifts:
            continue
        for day in range(1, num_days + 1):
            try:
                current_date = datetime(target_year, target_month, day)
            except ValueError:
                continue
            if current_date.date() > now_utc.date():
                continue
            weekday = current_date.weekday()
            if weekday not in _DIA_SEMANA_MAP:
                continue
            dia_enum = _DIA_SEMANA_MAP[weekday]
            for shift in [t for t in turma_shifts if t.dia == dia_enum]:
                expected_ref = f"{current_date.strftime('%Y-%m-%d')}_{shift.turno.value}"
                found = next((c for c in user_checkins if c.turno_referencia == expected_ref), None)
                data_hora = _fmt(found.hora_checkin) if found else current_date.strftime("%Y-%m-%d")
                aluno_rows.append(
                    [
                        user.nome,
                        user.email,
                        user.turma_ou_equipe,
                        user.patrimonio or "",
                        data_hora,
                        expected_ref,
                        _status_para(found, user.id, expected_ref),
                        (found.ip_publico or "") if found else "",
                    ]
                )

    aluno_header = ["Nome", "Email", "Turma", "Máquina", "Data/Hora", "Turno", "Status", "IP"]
    staff_header = ["Nome", "Email", "Máquina", "Data/Hora", "Turno", "Status", "IP"]

    if format == "excel":
        wb = openpyxl.Workbook()
        ws_staff = wb.active
        ws_staff.title = "Staff"
        ws_alunos = wb.create_sheet("Alunos")
        ws_staff.append(staff_header)
        ws_alunos.append(aluno_header)
        for row in staff_rows:
            ws_staff.append(row)
        for row in aluno_rows:
            ws_alunos.append(row)

        output_excel = io.BytesIO()
        wb.save(output_excel)
        output_excel.seek(0)
        return StreamingResponse(
            output_excel,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=checkins_lablivre_{target_year}_{target_month:02d}.xlsx"
            },
        )
    else:
        # CSV: mesma lógica de turnos esperados dos alunos; staff rotulado na coluna Turma.
        output_csv = io.StringIO()
        writer = csv.writer(output_csv)
        writer.writerow(aluno_header)
        for row in aluno_rows:
            writer.writerow(row)
        for sr in staff_rows:
            # Mapeia staff (7 col) para o layout de 8 colunas, com Turma="(Staff)"
            writer.writerow([sr[0], sr[1], "(Staff)", sr[2], sr[3], sr[4], sr[5], sr[6]])

        output_csv.seek(0)
        return StreamingResponse(
            iter([output_csv.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=checkins_lablivre.csv"},
        )


class JustificarRequest(BaseModel):
    data: str  # YYYY-MM-DD
    turno: str  # MANHA or TARDE


class RoleUpdateRequest(BaseModel):
    role: RoleAdmin


@router.post("/usuarios/{user_id}/role")
async def create_user_role(
    user_id: UUID,
    request: RoleUpdateRequest,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    # Regras de elevação de privilégio:
    # Apenas SUPER_ADMIN pode dar SUPER_ADMIN
    if request.role == RoleAdmin.SUPER_ADMIN and current_admin.role != RoleAdmin.SUPER_ADMIN:
        raise HTTPException(
            status_code=403, detail="Apenas Super Admins podem criar outros Super Admins"
        )

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.role = request.role
    await db.commit()
    return {"status": "sucesso", "role": user.role}


@router.post("/usuarios/{user_id}/justificar")
async def justificar_falta(
    user_id: UUID,
    request: JustificarRequest,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    # Verify user exists
    user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    turno_ref = f"{request.data}_{request.turno}"

    # Check if checkin already exists
    existing = await db.execute(
        select(CheckInModel).where(
            CheckInModel.user_id == user_id, CheckInModel.turno_referencia == turno_ref
        )
    )
    checkin = existing.scalars().first()

    if checkin:
        # Update existing
        checkin.status = StatusCheckin.JUSTIFICADO
    else:
        # Create new dummy checkin for the justification
        # Get the user's first device or create a mock web device
        # Note: device_id is required. We'll use a dummy ID or the admin's device?
        # A checkin needs a device. Let's create a generic "Admin Justification" device if none exists.

        dev_result = await db.execute(select(DeviceModel).where(DeviceModel.user_id == user_id))
        dev = dev_result.scalars().first()
        if not dev:
            dev = DeviceModel(
                id=uuid.uuid4(),
                user_id=user_id,
                mac_address="JUSTIFICADO_WEB",
                os_type="web",
                hostname="Painel_Admin",
                serial_number="N/A",
                principal=True,
            )
            db.add(dev)
            await db.flush()

        checkin = CheckInModel(
            user_id=user_id,
            device_id=dev.id,
            hora_checkin=datetime.now(UTC),  # Audit time
            status=StatusCheckin.JUSTIFICADO,
            turno_referencia=turno_ref,
            ip_publico="0.0.0.0",
        )
        db.add(checkin)

    await db.commit()
    return {"status": "sucesso", "mensagem": "Falta/Atraso justificado com sucesso."}


class UpdateRoleRequest(BaseModel):
    role: str


@router.put("/usuarios/{user_id}/role")
async def update_user_role_put(
    user_id: str,
    request: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    admin: UserModel = Depends(require_admin),
) -> dict[str, Any]:
    if admin.role != RoleAdmin.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Apenas Super Admins podem alterar cargos.")

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    try:
        user.role = RoleAdmin(request.role.upper())
        await db.commit()
    except ValueError:
        raise HTTPException(status_code=400, detail="Role inválida.") from None
    return {"status": "ok"}


class BulkIdsRequest(BaseModel):
    user_ids: list[UUID]


@router.post("/usuarios/bulk-aprovar")
async def bulk_aprovar_usuarios(
    request: BulkIdsRequest,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await db.execute(
        update(UserModel).where(UserModel.id.in_(request.user_ids)).values(admin_aprovado=True)
    )
    await db.commit()
    return {"message": f"{len(request.user_ids)} usuários aprovados"}


class BulkJustificarRequest(BaseModel):
    user_ids: list[UUID]
    data: str  # YYYY-MM-DD
    turno: str


@router.post("/usuarios/bulk-justificar")
async def bulk_justificar_faltas(
    request: BulkJustificarRequest,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    turno_ref = f"{request.data}_{request.turno}"
    count = 0
    now_utc = datetime.now(UTC)

    for uid in request.user_ids:
        # Check if checkin already exists
        existing = await db.execute(
            select(CheckInModel).where(
                CheckInModel.user_id == uid,
                CheckInModel.turno_referencia == turno_ref,
                CheckInModel.status != StatusCheckin.FALTA,
            )
        )
        if existing.scalars().first():
            continue

        dev = await db.execute(select(DeviceModel).where(DeviceModel.user_id == uid))
        device = dev.scalars().first()
        dev_id = device.id if device else None

        checkin = CheckInModel(
            user_id=uid,
            device_id=dev_id,
            hora_checkin=now_utc,
            ip_publico="127.0.0.1",
            status=StatusCheckin.JUSTIFICADO,
            turno_referencia=turno_ref,
            mensagem="Justificado em massa pelo painel",
        )
        db.add(checkin)
        count += 1

    await db.commit()
    return {"message": f"{count} faltas justificadas"}


class UpdateUserAdminRequest(BaseModel):
    turma_ou_equipe: str | None = None
    patrimonio: str | None = None
    tipo: TipoUsuario | None = None


@router.put("/usuarios/{user_id}")
async def admin_update_user(
    user_id: UUID,
    request: UpdateUserAdminRequest,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if request.turma_ou_equipe is not None:
        user.turma_ou_equipe = request.turma_ou_equipe
    if request.patrimonio is not None:
        user.patrimonio = request.patrimonio
    if request.tipo is not None:
        user.tipo = request.tipo

    await db.commit()
    return {"message": "Usuário atualizado com sucesso"}
