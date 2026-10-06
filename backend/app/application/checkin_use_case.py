from datetime import datetime, timezone
from uuid import uuid4, UUID
from app.domain.ports.checkin_repository import CheckInRepository
from app.domain.ports.user_repository import UserRepository
from app.domain.ports.device_repository import DeviceRepository
from app.domain.ports.config_repository import ConfigRepository
from app.domain.ports.geolocation_service import GeolocationService
from app.domain.ports.sheets_service import SheetsService

from app.domain.models import CheckIn, CheckInDuplicata, User, Device
from app.domain.enums import TipoUsuario, StatusCheckin
from app.domain.models import identificar_turno, calcular_status
from app.api.schemas.checkin_schemas import CheckinRequest
from app.domain.exceptions import (
    UsuarioInativoError, UsuarioNaoAprovadoError, DispositivoNaoRegistradoError,
    ForaDoRaioError, ForaTurnoError, DuplicataError
)
from app.config import settings

class CheckinUseCase:
    def __init__(
        self, 
        checkin_repo: CheckInRepository, 
        user_repo: UserRepository, 
        device_repo: DeviceRepository, 
        config_repo: ConfigRepository, 
        sheets_service: SheetsService, 
        geolocation_service: GeolocationService
    ):
        self.checkin_repo = checkin_repo
        self.user_repo = user_repo
        self.device_repo = device_repo
        self.config_repo = config_repo
        self.sheets_service = sheets_service
        self.geolocation_service = geolocation_service

    async def executar(self, request: CheckinRequest, user_id: UUID, ip_publico: str) -> tuple[CheckIn, str, User, Device]:
        user = await self.user_repo.buscar_por_id(user_id)
        if not user or not user.ativo:
            raise UsuarioInativoError("Usuário inativo")
        # Removendo admin_aprovado for now, so students can checkin directly. Or keep it? The logic was checking it.
        # if not user.admin_aprovado:
        #    raise UsuarioNaoAprovadoError("Usuário não aprovado")

        device = None
        if request.device_mac:
            device = await self.device_repo.buscar_por_mac(request.device_mac)
            if not device or device.user_id != user.id:
                raise DispositivoNaoRegistradoError("Dispositivo não registrado para este usuário")
        else:
            # Associa com qualquer dispositivo web virtual que o usuário tenha (criado no registro)
            devices = await self.device_repo.buscar_por_user(user.id)
            if devices:
                device = next((d for d in devices if d.os_type == "web"), devices[0])
            else:
                raise DispositivoNaoRegistradoError("Nenhum dispositivo registrado para este usuário")

        # Passar lat_user e lng_user se fornecidos na requisição
        esta_no_raio, dist = await self.geolocation_service.validar_localizacao(
            bssids=request.bssids or [], 
            lat_centro=settings.GEOFENCING_LAT, 
            lng_centro=settings.GEOFENCING_LNG, 
            raio_metros=settings.GEOFENCING_RADIUS_METERS,
            lat_user=request.lat,
            lng_user=request.lng
        )
        if not esta_no_raio:
            raise ForaDoRaioError(dist)

        now = datetime.now(timezone.utc)
        now_local = datetime.now() 
        
        turno = identificar_turno(user.turma_ou_equipe, now_local)
        # Desativado temporariamente:
        # if not turno and user.tipo == TipoUsuario.ALUNO:
        #     raise ForaTurnoError("Fora do horário de turno permitido")

        turno_ref = f"{now_local.strftime('%Y-%m-%d')}_{turno.turno.value}" if turno else f"{now_local.strftime('%Y-%m-%d')}_STAFF"

        checkin_existente = await self.checkin_repo.buscar_por_turno(user.id, turno_ref)
        if checkin_existente:
            duplicata = CheckInDuplicata(
                id=uuid4(),
                checkin_original_id=checkin_existente.id,
                user_id=user.id,
                device_id=device.id,
                hora_tentativa=now,
                motivo="DUPLICATA_MESMO_TURNO",
                ip_publico=ip_publico,
                criado_em=now
            )
            await self.checkin_repo.registrar_duplicata(duplicata)
            raise DuplicataError(checkin_existente.id, checkin_existente.hora_checkin)

        carencia_str = await self.config_repo.buscar('CARENCIA_MINUTOS')
        carencia_minutos = int(carencia_str) if carencia_str and carencia_str.isdigit() else 10

        status = StatusCheckin.PRESENTE
        if user.tipo == TipoUsuario.ALUNO and turno:
            status = calcular_status(now_local, turno.inicio, carencia_minutos)

        novo_checkin = CheckIn(
            id=uuid4(),
            user_id=user.id,
            device_id=device.id,
            hora_checkin=now,
            bssids=request.bssids or [],
            status=status,
            turno_referencia=turno_ref,
            exportado_sheets=False,
            criado_em=now,
            ip_publico=ip_publico,
            ssid=request.ssid
        )

        novo_checkin = await self.checkin_repo.criar(novo_checkin)

        return novo_checkin, "Ponto registrado com sucesso", user, device

    async def sync_to_sheets(self, checkin: CheckIn, user: User, device: Device):
        try:
            if user.tipo == TipoUsuario.ALUNO:
                sucesso = await self.sheets_service.exportar_checkin_aluno(checkin, user, device)
            else:
                sucesso = await self.sheets_service.exportar_checkin_staff(checkin, user, device)
            
            if sucesso:
                await self.checkin_repo.marcar_exportado(checkin.id)
        except Exception as e:
            print(f"Falha ao exportar em background: {e}")
