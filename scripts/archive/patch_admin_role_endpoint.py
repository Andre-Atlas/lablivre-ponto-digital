import re

with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

endpoint = """
class RoleUpdateRequest(BaseModel):
    role: RoleAdmin

@router.post("/usuarios/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    request: RoleUpdateRequest,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Regras de elevação de privilégio:
    # Apenas SUPER_ADMIN pode dar SUPER_ADMIN
    if request.role == RoleAdmin.SUPER_ADMIN and current_admin.role != RoleAdmin.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Apenas Super Admins podem criar outros Super Admins")
        
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    user.role = request.role
    await db.commit()
    return {"status": "sucesso", "role": user.role}
"""

if "class RoleUpdateRequest" not in content:
    content += endpoint

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
