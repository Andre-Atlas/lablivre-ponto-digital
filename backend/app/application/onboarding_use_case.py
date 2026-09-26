from uuid import uuid4
from datetime import datetime, timezone
from app.domain.ports.user_repository import UserRepository
from app.domain.ports.device_repository import DeviceRepository
from app.api.schemas.auth_schemas import OnboardingRequest
from app.domain.models import User, Device
from app.domain.enums import TipoUsuario
from app.domain.exceptions import EmailDuplicadoError, PatrimonioObrigatorioError
from app.adapters.auth.jwt_handler import create_access_token
from app.adapters.auth.oauth_google import verify_google_token
from app.adapters.auth.oauth_microsoft import verify_microsoft_token

class OnboardingUseCase:
    def __init__(self, user_repo: UserRepository, device_repo: DeviceRepository):
        self.user_repo = user_repo
        self.device_repo = device_repo

    async def executar(self, request: OnboardingRequest) -> tuple[User, str, bool]:
        # Validação do token OAuth
        if request.oauth_provider.lower() == "google":
            token_data = await verify_google_token(request.oauth_token)
        elif request.oauth_provider.lower() == "microsoft":
            token_data = await verify_microsoft_token(request.oauth_token)
        else:
            raise ValueError("Provider OAuth não suportado")
        
        email = token_data.get("email") or token_data.get("userPrincipalName")
        nome = token_data.get("name") or token_data.get("displayName", "")
        sub = token_data.get("sub") or token_data.get("id")

        if not email:
            raise ValueError("Token não contém email")

        usuario_existente = await self.user_repo.buscar_por_email(email)
        if usuario_existente:
            # Verifica se o dispositivo atual está registrado para este usuário
            dispositivos_do_usuario = await self.device_repo.buscar_por_user(usuario_existente.id)
            mac_existente = any(d.mac_address == request.device_mac for d in dispositivos_do_usuario)
            
            if not mac_existente:
                from uuid import uuid4
                from datetime import datetime, timezone
                from app.domain.models import Device
                
                novo_device = Device(
                    id=uuid4(),
                    user_id=usuario_existente.id,
                    mac_address=request.device_mac,
                    os_type=request.device_os,
                    hostname=request.device_hostname,
                    serial_number=request.device_serial,
                    principal=len(dispositivos_do_usuario) == 0,
                    registrado_em=datetime.now(timezone.utc)
                )
                await self.device_repo.criar(novo_device)

            jwt_token = create_access_token(data={
                "sub": str(usuario_existente.id), 
                "tipo": str(usuario_existente.tipo)
            })
            return usuario_existente, jwt_token, False

        # Validação de dados para novos usuários
        if request.tipo == TipoUsuario.ALUNO:
            if not request.patrimonio:
                raise PatrimonioObrigatorioError("Patrimônio é obrigatório para alunos.")
            if not request.turma_ou_equipe:
                raise ValueError("Turma/Equipe é obrigatória para novos alunos.")
        
        now = datetime.now(timezone.utc)

        novo_usuario = User(
            id=uuid4(),
            email=email,
            nome=nome,
            tipo=request.tipo,
            turma_ou_equipe=request.turma_ou_equipe or "STAFF",
            oauth_provider=request.oauth_provider.lower(),
            oauth_sub=sub,
            patrimonio=request.patrimonio,
            ativo=True,
            admin_aprovado=False,
            criado_em=now,
            atualizado_em=now
        )
        
        novo_device = Device(
            id=uuid4(),
            user_id=novo_usuario.id,
            mac_address=request.device_mac,
            os_type=request.device_os,
            hostname=request.device_hostname,
            serial_number=request.device_serial,
            principal=True,
            registrado_em=now
        )

        await self.user_repo.criar(novo_usuario)
        await self.device_repo.criar(novo_device)

        jwt_token = create_access_token(data={
            "sub": str(novo_usuario.id), 
            "tipo": str(novo_usuario.tipo)
        })

        return novo_usuario, jwt_token, True
