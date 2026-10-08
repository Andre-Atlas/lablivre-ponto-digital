import re
with open("backend/app/api/schemas/admin_schemas.py", "r") as f:
    content = f.read()

if "role:" not in content:
    content = content.replace("tipo: TipoUsuario", "tipo: TipoUsuario\n    role: Optional[str] = None")
    
with open("backend/app/api/schemas/admin_schemas.py", "w") as f:
    f.write(content)
