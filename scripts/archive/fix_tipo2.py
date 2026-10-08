with open("backend/app/api/v1/router_checkin.py", "r") as f:
    content = f.read()
    
content = content.replace("from sqlalchemy import select\nfrom uuid import UUID", "from sqlalchemy import select\nfrom uuid import UUID\nfrom app.domain.enums import TipoUsuario, StatusCheckin")

with open("backend/app/api/v1/router_checkin.py", "w") as f:
    f.write(content)
