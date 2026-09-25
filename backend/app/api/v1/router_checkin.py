from fastapi import APIRouter, Depends, Request, HTTPException, status, BackgroundTasks
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
