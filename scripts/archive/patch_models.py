import re

with open("backend/app/domain/models.py", "r") as f:
    content = f.read()
if "role: RoleAdmin" not in content:
    content = content.replace("tipo: TipoUsuario", "tipo: TipoUsuario\n    role: RoleAdmin = field(default=RoleAdmin.NONE)")
    content = content.replace("from .enums import TipoUsuario, StatusCheckin, DiaSemana, Turno", "from .enums import TipoUsuario, StatusCheckin, DiaSemana, Turno, RoleAdmin")
with open("backend/app/domain/models.py", "w") as f:
    f.write(content)

with open("backend/app/adapters/persistence/orm_models.py", "r") as f:
    orm_content = f.read()
if "role: Mapped[RoleAdmin]" not in orm_content:
    orm_content = orm_content.replace("tipo: Mapped[TipoUsuario] = mapped_column(SAEnum(TipoUsuario), nullable=False)", "tipo: Mapped[TipoUsuario] = mapped_column(SAEnum(TipoUsuario), nullable=False)\n    role: Mapped[RoleAdmin] = mapped_column(SAEnum(RoleAdmin), default=RoleAdmin.NONE, server_default='NONE', nullable=False)")
    orm_content = orm_content.replace("from app.domain.enums import TipoUsuario", "from app.domain.enums import TipoUsuario, RoleAdmin")
with open("backend/app/adapters/persistence/orm_models.py", "w") as f:
    f.write(orm_content)
