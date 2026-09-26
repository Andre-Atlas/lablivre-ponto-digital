with open("backend/app/api/v1/router_checkin.py", "r") as f:
    content = f.read()

if "from app.domain.enums import" not in content:
    content = content.replace("from sqlalchemy import select", "from sqlalchemy import select\nfrom app.domain.enums import TipoUsuario, StatusCheckin")

with open("backend/app/api/v1/router_checkin.py", "w") as f:
    f.write(content)
