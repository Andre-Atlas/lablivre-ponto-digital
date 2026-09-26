from fastapi import APIRouter, Depends, Request, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from uuid import UUID
from app.domain.enums import TipoUsuario, StatusCheckin
from app.adapters.persistence.orm_models import User as UserModel, Device as DeviceModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.schemas.checkin_schemas import CheckinRequest, CheckinResponse
from app.api.middleware.auth_dependencies import get_current_user
from app.application.checkin_use_case import CheckinUseCase
from app.adapters.persistence.checkin_repo_impl import CheckInRepositoryImpl
from app.adapters.persistence.user_repo_impl import UserRepositoryImpl
from app.adapters.persistence.device_repo_impl import DeviceRepositoryImpl
from app.adapters.persistence.config_repo_impl import ConfigRepositoryImpl
from app.adapters.persistence.database import get_db, async_session_maker

from app.adapters.external.geolocation_service_impl import GeolocationServiceImpl
from app.adapters.external.sheets_service_impl import SheetsServiceImpl

from app.domain.exceptions import (
    UsuarioInativoError, UsuarioNaoAprovadoError, DispositivoNaoRegistradoError,
    ForaDoRaioError, ForaTurnoError, DuplicataError
)
from app.domain.models import CheckIn, User, Device

router = APIRouter(prefix="/checkin", tags=["Check-in"])

async def background_sheets_export(checkin: CheckIn, user: User, device: Device):
    """Executado em background com sua própria sessão de banco de dados."""
    async with async_session_maker() as db:
        use_case = CheckinUseCase(
            checkin_repo=CheckInRepositoryImpl(db),
            user_repo=UserRepositoryImpl(db),
            device_repo=DeviceRepositoryImpl(db),
            config_repo=ConfigRepositoryImpl(db),
            sheets_service=SheetsServiceImpl(),
            geolocation_service=GeolocationServiceImpl()
        )
        await use_case.sync_to_sheets(checkin, user, device)
        await db.commit()

@router.post("/", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
async def registrar_checkin(
    request: Request,
    checkin_req: CheckinRequest,
    background_tasks: BackgroundTasks,
    user_payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ip_publico = request.client.host if request.client else "127.0.0.1"

    use_case = CheckinUseCase(
        checkin_repo=CheckInRepositoryImpl(db),
        user_repo=UserRepositoryImpl(db),
        device_repo=DeviceRepositoryImpl(db),
        config_repo=ConfigRepositoryImpl(db),
        sheets_service=SheetsServiceImpl(),
        geolocation_service=GeolocationServiceImpl()
    )

    try:
        user_id = UUID(user_payload["sub"])
        checkin, mensagem, user, device = await use_case.executar(
            request=checkin_req,
            user_id=user_id,
            ip_publico=ip_publico
        )
        
        await db.commit()
        
        # Agenda exportação em background
        background_tasks.add_task(background_sheets_export, checkin, user, device)
        
        return CheckinResponse(
            status_checkin=checkin.status.value,
            turno=checkin.turno_referencia,
            mensagem=mensagem,
            hora_registrada=checkin.hora_checkin
        )

    except DuplicataError as e:
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Você já bateu o ponto neste turno"
        )
    except (UsuarioInativoError, UsuarioNaoAprovadoError, DispositivoNaoRegistradoError) as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (ForaDoRaioError, ForaTurnoError) as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

from pydantic import BaseModel
class WebCheckinRequest(BaseModel):
    lat: float
    lng: float

@router.post("/web", status_code=status.HTTP_201_CREATED)
async def checkin_web(
    request: WebCheckinRequest,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token inválido")
        
    user_id = UUID(user_id_str)
    
    # 1. Fetch user
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    if user.tipo != TipoUsuario.STAFF:
        raise HTTPException(status_code=403, detail="Check-in Web permitido apenas para STAFF")
        
    if not user.admin_aprovado:
        raise HTTPException(status_code=403, detail="Usuário não aprovado pelo administrador")

    # TODO: Register check-in logically (using CheckinUseCase but bypassing geofence logic, 
    # or just saving it here). Since STAFF doesn't have strict time/geofence constraints, 
    # we can just register the check-in immediately.
    
    from datetime import datetime, timezone
    from app.adapters.persistence.orm_models import Checkin as CheckinModel
    from app.domain.enums import StatusCheckin
    
    # For STAFF we don't have Turno constraints strictly, but we need a 'turno_referencia'.
    # We can use the current date as reference.
    now = datetime.now(timezone.utc)
    turno_ref = now.strftime("%Y-%m-%d_STAFF")
    
    checkin = CheckinModel(
        user_id=user.id,
        # We need a device_id. For web, maybe they have a registered web device?
        # Let's see if they have any device
        device_id=None, 
        hora_checkin=now,
        ip_publico=f"{request.lat},{request.lng}", # reuse ip_publico for coordinates for now or let it null
        status=StatusCheckin.PRESENTE,
        turno_referencia=turno_ref
    )
    
    # Wait, device_id is required (nullable=False)
    if not checkin.device_id:
        # fetch their device
        dev_res = await db.execute(select(DeviceModel).where(DeviceModel.user_id == user.id))
        dev = dev_res.scalars().first()
        if not dev:
            # Auto-register a Web Device for STAFF
            import uuid
            new_dev = DeviceModel(id=uuid.uuid4(), user_id=user.id, mac_address="web-browser-" + str(uuid.uuid4())[:8], os_type="web", hostname="dashboard", serial_number="web")
            db.add(new_dev)
            await db.commit() # commit to get id
            checkin.device_id = new_dev.id
        else:
            checkin.device_id = dev.id
        
    db.add(checkin)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        # might be duplicate (unique constraint on user_id, turno_referencia)
        if "uq_checkin_user_turno" in str(e):
            raise HTTPException(status_code=409, detail="Você já bateu o ponto hoje")
        raise
        
    return {"status": "sucesso", "mensagem": "Ponto registrado (STAFF Web)"}
