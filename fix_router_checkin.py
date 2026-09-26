with open("backend/app/api/v1/router_checkin.py", "r") as f:
    content = f.read()

imports = """
from sqlalchemy import select
from uuid import UUID
from app.adapters.persistence.orm_models import User as UserModel, Device as DeviceModel
"""

if "from sqlalchemy import select" not in content:
    content = content.replace("from fastapi import APIRouter", "from fastapi import APIRouter\n" + imports)

with open("backend/app/api/v1/router_checkin.py", "w") as f:
    f.write(content)
