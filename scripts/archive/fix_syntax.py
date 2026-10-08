with open("backend/app/api/v1/router_checkin.py", "r") as f:
    content = f.read()

content = content.replace("from fastapi import APIRouter\n\nfrom sqlalchemy import select\nfrom uuid import UUID\nfrom app.adapters.persistence.orm_models import User as UserModel, Device as DeviceModel\n, Depends, Request, HTTPException, status, BackgroundTasks", "from fastapi import APIRouter, Depends, Request, HTTPException, status, BackgroundTasks\nfrom sqlalchemy import select\nfrom uuid import UUID\nfrom app.adapters.persistence.orm_models import User as UserModel, Device as DeviceModel")

with open("backend/app/api/v1/router_checkin.py", "w") as f:
    f.write(content)
