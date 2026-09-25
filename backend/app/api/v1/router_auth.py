from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.auth_schemas import OnboardingRequest, OnboardingResponse
from app.application.onboarding_use_case import OnboardingUseCase
from app.domain.exceptions import EmailDuplicadoError, PatrimonioObrigatorioError
from app.adapters.persistence.user_repo_impl import UserRepositoryImpl
from app.adapters.persistence.device_repo_impl import DeviceRepositoryImpl
from app.adapters.persistence.database import get_db
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/onboarding", response_model=OnboardingResponse)
async def onboarding(request: OnboardingRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepositoryImpl(db)
    device_repo = DeviceRepositoryImpl(db)
    use_case = OnboardingUseCase(user_repo=user_repo, device_repo=device_repo)
    
    try:
        user, token, is_new = await use_case.executar(request)
        await db.commit()
        
        status_msg = "PENDENTE_APROVACAO" if not user.admin_aprovado else "APROVADO"
        
        resp_data = OnboardingResponse(
            status=status_msg,
            access_token=token,
            user_id=user.id
        )
        
        # Retorna 201 se foi criado agora, ou 200 se já existia
        return JSONResponse(status_code=201 if is_new else 200, content=resp_data.model_dump(mode='json'))
        
    except EmailDuplicadoError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PatrimonioObrigatorioError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        await db.rollback()
        print("ValueError no onboarding:", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        print("Erro no onboarding:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

from pydantic import BaseModel
from app.domain.enums import TipoUsuario
from app.adapters.auth.jwt_handler import create_access_token

from app.utils.security import verify_password

class AdminLoginRequest(BaseModel):
    email: str
    password: str

@router.post("/admin-login")
async def admin_login(request: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepositoryImpl(db)
    user = await user_repo.buscar_por_email(request.email)
    
    if not user or user.tipo != TipoUsuario.STAFF:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas administradores")
        
    if not user.senha_hash or not verify_password(request.password, user.senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")
        
    token = create_access_token(data={"sub": str(user.id), "tipo": user.tipo.value})
    return {"access_token": token, "user_id": user.id}
