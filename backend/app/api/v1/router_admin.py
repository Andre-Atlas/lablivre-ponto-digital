from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from app.adapters.persistence.database import get_db
from app.adapters.persistence.orm_models import User as UserModel
from app.api.middleware.auth_dependencies import get_current_user
from app.domain.models import User
from app.domain.enums import TipoUsuario

router = APIRouter(prefix="/admin", tags=["Administração"])

class UserAdminResponse(BaseModel):
    id: UUID
    nome: str
    email: str
    tipo: TipoUsuario
    admin_aprovado: bool

async def require_admin(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token inválido")
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido")
        
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    current_user = result.scalars().first()
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    if current_user.tipo != TipoUsuario.STAFF:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
    return current_user

@router.get("/usuarios", response_model=list[UserAdminResponse])
async def list_usuarios(
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return [
        UserAdminResponse(
            id=u.id, 
            nome=u.nome, 
            email=u.email, 
            tipo=u.tipo, 
            admin_aprovado=u.admin_aprovado
        ) for u in users
    ]

@router.post("/usuarios/{user_id}/aprovar")
async def aprovar_usuario(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user_model = result.scalars().first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        
    user_model.admin_aprovado = True
    await db.commit()
    return {"message": f"Usuário {user_model.nome} aprovado com sucesso."}

from pydantic import EmailStr

from app.utils.security import get_password_hash

class CreateAdminRequest(BaseModel):
    nome: str
    email: str
    senha: str

@router.post("/usuarios")
async def create_admin(
    request: CreateAdminRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # Verify email uniqueness
    existing = await db.execute(select(UserModel).where(UserModel.email == request.email))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    
    import uuid
    new_admin = UserModel(
        email=request.email,
        nome=request.nome,
        tipo=TipoUsuario.STAFF,
        turma_ou_equipe="Administração",
        oauth_provider="manual",
        oauth_sub=f"manual_{uuid.uuid4()}",
        admin_aprovado=True,
        senha_hash=get_password_hash(request.senha)
    )
    db.add(new_admin)
    await db.commit()
    return {"message": f"Administrador {new_admin.nome} criado com sucesso."}

@router.delete("/usuarios/{user_id}")
async def delete_usuario(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user_model = result.scalars().first()
    
    if not user_model:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    if user_model.id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta.")
        
    await db.delete(user_model)
    await db.commit()
    return {"message": "Usuário excluído com sucesso."}

import csv
import io
from fastapi.responses import StreamingResponse
from app.adapters.persistence.orm_models import Checkin as CheckInModel

@router.get("/export/usuarios")
async def export_usuarios(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Nome", "Email", "Tipo", "Aprovado", "Turma", "Criado Em"])
    
    for u in users:
        writer.writerow([
            str(u.id), u.nome, u.email, u.tipo.value if u.tipo else "",
            "Sim" if u.admin_aprovado else "Nao", u.turma_ou_equipe or "",
            u.criado_em.strftime("%Y-%m-%d %H:%M:%S") if u.criado_em else ""
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=usuarios_lablivre.csv"}
    )

from typing import Optional
@router.get("/export/checkins")
async def export_checkins(tipo: Optional[TipoUsuario] = None, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    query = select(CheckInModel, UserModel).join(UserModel, CheckInModel.user_id == UserModel.id)
    if tipo:
        query = query.where(UserModel.tipo == tipo)
    query = query.order_by(CheckInModel.hora_checkin.desc())
    result = await db.execute(query)
    rows = result.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Email", "Data/Hora", "Turno", "Status", "IP", "Lat", "Lng"])
    
    for checkin, user in rows:
        writer.writerow([
            user.nome, user.email,
            checkin.hora_checkin.strftime("%Y-%m-%d %H:%M:%S") if checkin.hora_checkin else "",
            checkin.turno_referencia or "",
            checkin.status.value if checkin.status else "",
            checkin.ip_publico or "",
            "",
            ""
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pontos_lablivre.csv"}
    )
