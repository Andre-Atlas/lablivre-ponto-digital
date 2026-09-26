with open("backend/app/api/v1/router_admin.py", "r") as f:
    content = f.read()

import re

# Update export_checkins
old_export_checkins = """@router.get("/export/checkins")
async def export_checkins(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(
        select(CheckInModel, UserModel)
        .join(UserModel, CheckInModel.user_id == UserModel.id)
        .order_by(CheckInModel.hora_checkin.desc())
    )"""

new_export_checkins = """from typing import Optional
@router.get("/export/checkins")
async def export_checkins(tipo: Optional[TipoUsuario] = None, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    query = select(CheckInModel, UserModel).join(UserModel, CheckInModel.user_id == UserModel.id)
    if tipo:
        query = query.where(UserModel.tipo == tipo)
    query = query.order_by(CheckInModel.hora_checkin.desc())
    result = await db.execute(query)"""

content = content.replace(old_export_checkins, new_export_checkins)

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
