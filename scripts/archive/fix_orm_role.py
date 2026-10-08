with open("backend/app/adapters/persistence/orm_models.py", "r") as f:
    content = f.read()

# Add NONE to RoleAdmin in orm_models
content = content.replace("VIEWER = 'VIEWER'", "VIEWER = 'VIEWER'\n    NONE = 'NONE'")

# Actually the replace in patch_models might have failed if it was already patched? No, let's check if `role:` is in User
if "role: Mapped[RoleAdmin]" not in content:
    content = content.replace("tipo: Mapped[TipoUsuario] = mapped_column(SAEnum(TipoUsuario), nullable=False)", "tipo: Mapped[TipoUsuario] = mapped_column(SAEnum(TipoUsuario), nullable=False)\n    role: Mapped[RoleAdmin] = mapped_column(SAEnum(RoleAdmin), default=RoleAdmin.NONE, server_default='NONE', nullable=False)")

with open("backend/app/adapters/persistence/orm_models.py", "w") as f:
    f.write(content)
