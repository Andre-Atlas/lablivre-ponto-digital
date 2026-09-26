with open("backend/app/adapters/persistence/orm_models.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "tipo: Mapped[TipoUsuario]" in line and "role: Mapped[RoleAdmin]" not in line:
        new_lines.append("    role: Mapped[RoleAdmin] = mapped_column(SAEnum(RoleAdmin), default=RoleAdmin.NONE, server_default='NONE', nullable=False)\n")

with open("backend/app/adapters/persistence/orm_models.py", "w") as f:
    f.writelines(new_lines)
