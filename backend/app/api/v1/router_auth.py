from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.database import get_db
from app.adapters.persistence.device_repo_impl import DeviceRepositoryImpl
from app.adapters.persistence.user_repo_impl import UserRepositoryImpl
from app.api.schemas.auth_schemas import (
    LoginRequest,
    OnboardingRequest,
    OnboardingResponse,
    RegisterRequest,
)
from app.application.onboarding_use_case import OnboardingUseCase
from app.domain.exceptions import EmailDuplicadoError, PatrimonioObrigatorioError

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/onboarding", response_model=OnboardingResponse)
async def onboarding(request: OnboardingRequest, db: AsyncSession = Depends(get_db)) -> Any:
    user_repo = UserRepositoryImpl(db)
    device_repo = DeviceRepositoryImpl(db)
    use_case = OnboardingUseCase(user_repo=user_repo, device_repo=device_repo)

    try:
        user, token, is_new = await use_case.executar(request)
        await db.commit()

        status_msg = "PENDENTE_APROVACAO" if not user.admin_aprovado else "APROVADO"

        resp_data = OnboardingResponse(status=status_msg, access_token=token, user_id=user.id)

        return JSONResponse(
            status_code=201 if is_new else 200, content=resp_data.model_dump(mode="json")
        )

    except EmailDuplicadoError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except PatrimonioObrigatorioError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except ValueError as e:
        await db.rollback()
        print("ValueError no onboarding:", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        await db.rollback()
        print("Erro no onboarding:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


import uuid
from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy.future import select

from app.adapters.auth.jwt_handler import create_access_token
from app.adapters.persistence.orm_models import Device as DeviceORM
from app.adapters.persistence.orm_models import User as UserORM
from app.domain.enums import RoleAdmin, TipoUsuario
from app.utils.security import get_password_hash, verify_password


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> Any:
    result = await db.execute(select(UserORM).where(UserORM.email == request.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not user.senha_hash or not verify_password(request.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    if not user.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")

    is_admin = user.role in [RoleAdmin.SUPER_ADMIN, RoleAdmin.ADMIN]
    tipo_resposta = "ADMIN" if is_admin else user.tipo.value

    token = create_access_token(
        data={
            "sub": str(user.id),
            "tipo": tipo_resposta,
            "role": user.role.value if user.role else RoleAdmin.NONE.value,
        }
    )
    return {"access_token": token, "user_id": user.id, "tipo": tipo_resposta}


@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)) -> Any:
    result = await db.execute(select(UserORM).where(UserORM.email == request.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    new_user = UserORM(
        id=uuid.uuid4(),
        nome=request.nome,
        email=request.email,
        tipo=TipoUsuario.ALUNO,
        turma_ou_equipe=request.turma,
        patrimonio=str(request.numero_maquina),
        ativo=True,
        admin_aprovado=False,  # Precisa de aprovação? Depende da sua regra. Deixaremos False por segurança
        criado_em=datetime.now(UTC),
        role=RoleAdmin.NONE,
        senha_hash=get_password_hash(request.senha),
        oauth_provider="local",
        oauth_sub="",
    )
    db.add(new_user)

    # Criar um Device Virtual para web
    new_device = DeviceORM(
        id=uuid.uuid4(),
        user_id=new_user.id,
        mac_address=f"web_{uuid.uuid4().hex[:13]}",
        os_type="web",
        registrado_em=datetime.now(UTC),
    )
    db.add(new_device)

    await db.commit()
    return {"message": "Cadastro realizado com sucesso", "user_id": new_user.id}


from app.api.middleware.auth_dependencies import get_current_user


class UpdateNomeRequest(BaseModel):
    nome: str


@router.put("/me")
async def update_nome(
    request: UpdateNomeRequest,
    user_payload: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    user_id = user_payload["sub"]
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.nome = request.nome
    await db.commit()
    return {"message": "Nome atualizado com sucesso", "nome": user.nome}


class UpdateSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str


@router.put("/me/senha")
async def update_senha(
    request: UpdateSenhaRequest,
    user_payload: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    user_id = user_payload["sub"]
    result = await db.execute(select(UserORM).where(UserORM.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not user.senha_hash or not verify_password(request.senha_atual, user.senha_hash):
        raise HTTPException(status_code=401, detail="Senha atual incorreta")

    user.senha_hash = get_password_hash(request.nova_senha)
    await db.commit()
    return {"message": "Senha atualizada com sucesso"}
