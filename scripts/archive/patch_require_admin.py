with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

content = content.replace("from app.domain.enums import TipoUsuario", "from app.domain.enums import TipoUsuario, RoleAdmin")

old_check = """    if current_user.tipo != TipoUsuario.STAFF:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")"""

new_check = """    if current_user.role not in [RoleAdmin.SUPER_ADMIN, RoleAdmin.ADMIN]:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")"""

content = content.replace(old_check, new_check)

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
