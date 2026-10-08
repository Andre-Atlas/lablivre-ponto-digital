with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

# Update CreateAdminRequest
import re
new_req = """class CreateAdminRequest(BaseModel):
    nome: str
    email: str
    senha: str
    role: str = "STAFF" """
content = re.sub(r'class CreateAdminRequest\(BaseModel\):\s+nome: str\s+email: str\s+senha: str', new_req, content)

# Update POST /usuarios
old_post = """    new_admin = UserModel(
        email=request.email,
        nome=request.nome,
        tipo=TipoUsuario.STAFF,
        turma_ou_equipe="Administração",
        oauth_provider="manual",
        oauth_sub=f"manual_{uuid.uuid4()}",
        admin_aprovado=True,
        senha_hash=get_password_hash(request.senha)
    )"""
new_post = """    new_admin = UserModel(
        email=request.email,
        nome=request.nome,
        tipo=TipoUsuario.STAFF,
        role=RoleAdmin(request.role.upper()) if request.role else RoleAdmin.STAFF,
        turma_ou_equipe="Administração",
        oauth_provider="manual",
        oauth_sub=f"manual_{uuid.uuid4()}",
        admin_aprovado=True,
        senha_hash=get_password_hash(request.senha)
    )"""
content = content.replace(old_post, new_post)

# Add PUT /usuarios/{id}/role
put_role = """
class UpdateRoleRequest(BaseModel):
    role: str

@router.put("/usuarios/{user_id}/role")
async def update_user_role(
    user_id: str,
    request: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    admin: UserORM = Depends(require_admin)
):
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
        raise HTTPException(status_code=400, detail="Role inválida.")
    return {"status": "ok"}
"""
content += put_role

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
