with open('backend/app/api/v1/router_auth.py', 'r') as f:
    content = f.read()

import_stmt = "from app.adapters.persistence.orm_models import User as UserORM\nfrom sqlalchemy.future import select\n"
if "UserORM" not in content:
    content = content.replace("from app.utils.security import verify_password", import_stmt + "from app.utils.security import verify_password")

old_query = """    user_repo = UserRepositoryImpl(db)
    user = await user_repo.buscar_por_email(request.email)
    
    if not user or user.tipo != TipoUsuario.STAFF:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas administradores")
        
    if not user.senha_hash or not verify_password(request.password, user.senha_hash):"""

new_query = """    result = await db.execute(select(UserORM).where(UserORM.email == request.email))
    user = result.scalars().first()
    
    if not user or user.tipo != TipoUsuario.STAFF:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas administradores")
        
    if not user.senha_hash or not verify_password(request.password, user.senha_hash):"""

content = content.replace(old_query, new_query)

with open('backend/app/api/v1/router_auth.py', 'w') as f:
    f.write(content)
