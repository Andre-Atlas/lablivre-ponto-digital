import re

with open("backend/app/domain/models.py", "r") as f:
    content = f.read()

# I will move `role: RoleAdmin = field(default=RoleAdmin.NONE)` to the end of the non-default fields. Or just provide it later.
# In `User`:
#     id: UUID
#     email: str
#     nome: str
#     tipo: TipoUsuario
#     role: RoleAdmin = field(default=RoleAdmin.NONE)
#     turma_ou_equipe: str
# I will change `role` to not have a default, or move it after `atualizado_em`

content = content.replace("    tipo: TipoUsuario\n    role: RoleAdmin = field(default=RoleAdmin.NONE)\n    turma_ou_equipe: str", "    tipo: TipoUsuario\n    turma_ou_equipe: str")
content = content.replace("    atualizado_em: datetime", "    atualizado_em: datetime\n    role: RoleAdmin = field(default=RoleAdmin.NONE)")

with open("backend/app/domain/models.py", "w") as f:
    f.write(content)
