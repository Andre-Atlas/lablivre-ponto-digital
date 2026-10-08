from __future__ import annotations

import calendar
import csv
import io
import uuid
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import openpyxl
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.database import get_db
from app.adapters.persistence.orm_models import Checkin as CheckInModel
from app.adapters.persistence.orm_models import Device as DeviceModel
from app.adapters.persistence.orm_models import User as UserModel
from app.api.middleware.auth_dependencies import get_current_user
from app.domain.enums import RoleAdmin, StatusCheckin, TipoUsuario
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
async def list_usuarios(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)) -> Any:
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return users  # Let FastAPI serialize it. We just need from_attributes=True in schema.


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
async def export_usuarios(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)) -> Any:
    result = await db.execute(select(UserModel))
    users = result.scalars().all()

    output_csv = io.StringIO()
    writer = csv.writer(output_csv)
    writer.writerow(["ID", "Nome", "Email", "Tipo", "Aprovado", "Turma", "Máquina", "Criado Em"])

    for u in users:
        writer.writerow(
            [
                str(u.id),
                u.nome,
                u.email,
                u.tipo.value if u.tipo else "",
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

    if format == "excel":
        wb = openpyxl.Workbook()
        ws_staff = wb.active
        ws_staff.title = "Staff"
        ws_alunos = wb.create_sheet("Alunos")

        ws_staff.append(["Nome", "Email", "Máquina", "Data/Hora", "Turno", "Status", "IP"])
        ws_alunos.append(
            ["Nome", "Email", "Turma", "Máquina", "Data/Hora", "Turno", "Status", "IP"]
        )

        # Organize checkins by user and day/turno
        checkins_by_user: dict[Any, Any] = {}
        for checkin, user in rows:
            if user.id not in checkins_by_user:
                checkins_by_user[user.id] = []
            checkins_by_user[user.id].append(checkin)

        # Fetch all users to calculate faltas even for those who didn't check in at all
        users_result = await db.execute(select(UserModel))
        all_users = users_result.scalars().all()

        from app.domain.models import _DIA_SEMANA_MAP, TURNOS_ALUNOS

        # Determine valid days in the target month up to today
        num_days = calendar.monthrange(target_year, target_month)[1]

        for user in all_users:
            if tipo and user.tipo != tipo:
                continue

            user_checkins = checkins_by_user.get(user.id, [])

            if user.tipo == TipoUsuario.STAFF:
                # Just dump raw checkins for Staff
                for checkin in user_checkins:
                    # Filter by month/year (approx)
                    if (
                        checkin.hora_checkin.year == target_year
                        and checkin.hora_checkin.month == target_month
                    ):
                        ws_staff.append(
                            [
                                user.nome,
                                user.email,
                                user.patrimonio or "",
                                checkin.hora_checkin.replace(tzinfo=UTC)
                                .astimezone(timezone(timedelta(hours=-3)))
                                .strftime("%Y-%m-%d %H:%M:%S")
                                if checkin.hora_checkin
                                else "",
                                checkin.turno_referencia or "",
                                checkin.status.value if checkin.status else "",
                                checkin.ip_publico or "",
                            ]
                        )
            else:
                # ALUNO: Calculate Faltas
                if not user.turma_ou_equipe:
                    continue

                # Find the shifts for this turma
                turma_shifts = [t for t in TURNOS_ALUNOS if t.turma == user.turma_ou_equipe]
                if not turma_shifts:
                    continue

                # Check each day of the month
                for day in range(1, num_days + 1):
                    try:
                        current_date = datetime(target_year, target_month, day)
                    except ValueError:
                        continue

                    # Don't calculate faltas for future days
                    if current_date.date() > now_utc.date():
                        continue

                    weekday = current_date.weekday()
                    if weekday not in _DIA_SEMANA_MAP:
                        continue

                    dia_enum = _DIA_SEMANA_MAP[weekday]

                    # Expected shifts for this day
                    expected_shifts = [t for t in turma_shifts if t.dia == dia_enum]

                    for shift in expected_shifts:
                        # Find if user has checkin for this shift
                        # turno_referencia is usually "{YYYY-MM-DD}_{MANHA/TARDE}"
                        expected_ref = f"{current_date.strftime('%Y-%m-%d')}_{shift.turno.value}"

                        found_checkin = next(
                            (c for c in user_checkins if c.turno_referencia == expected_ref), None
                        )

                        if found_checkin:
                            ws_alunos.append(
                                [
                                    user.nome,
                                    user.email,
                                    user.turma_ou_equipe,
                                    user.patrimonio or "",
                                    found_checkin.hora_checkin.replace(tzinfo=UTC)
                                    .astimezone(timezone(timedelta(hours=-3)))
                                    .strftime("%Y-%m-%d %H:%M:%S")
                                    if found_checkin.hora_checkin
                                    else "",
                                    expected_ref,
                                    found_checkin.status.value if found_checkin.status else "",
                                    found_checkin.ip_publico or "",
                                ]
                            )
                        else:
                            # Falta!
                            ws_alunos.append(
                                [
                                    user.nome,
                                    user.email,
                                    user.turma_ou_equipe,
                                    user.patrimonio or "",
                                    current_date.strftime("%Y-%m-%d"),
                                    expected_ref,
                                    "FALTA",
                                    "",
                                ]
                            )

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
        # Default CSV
        output_csv = io.StringIO()
        writer = csv.writer(output_csv)
        writer.writerow(["Nome", "Email", "Turma", "Máquina", "Data/Hora", "Turno", "Status", "IP"])

        for checkin, user in rows:
            writer.writerow(
                [
                    user.nome,
                    user.email,
                    user.turma_ou_equipe or "",
                    user.patrimonio or "",
                    checkin.hora_checkin.replace(tzinfo=UTC)
                    .astimezone(timezone(timedelta(hours=-3)))
                    .strftime("%Y-%m-%d %H:%M:%S")
                    if checkin.hora_checkin
                    else "",
                    checkin.turno_referencia or "",
                    checkin.status.value if checkin.status else "",
                    checkin.ip_publico or "",
                ]
            )

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
