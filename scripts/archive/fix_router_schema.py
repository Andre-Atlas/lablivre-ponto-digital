import re

with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

# Make sure ConfigDict and Optional are imported
if "ConfigDict" not in content:
    content = content.replace("from pydantic import BaseModel", "from pydantic import BaseModel, ConfigDict\nfrom typing import Optional")

old_schema = """class UserAdminResponse(BaseModel):
    id: UUID
    nome: str
    email: str
    tipo: TipoUsuario
    admin_aprovado: bool"""

new_schema = """class UserAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    email: str
    tipo: TipoUsuario
    role: Optional[RoleAdmin] = None
    admin_aprovado: bool"""

content = content.replace(old_schema, new_schema)

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
