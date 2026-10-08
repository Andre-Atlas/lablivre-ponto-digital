with open("backend/app/api/v1/router_checkin.py", "r") as f:
    content = f.read()

endpoint = """
from pydantic import BaseModel
class WebCheckinRequest(BaseModel):
    lat: float
    lng: float

@router.post("/web", status_code=status.HTTP_201_CREATED)
async def checkin_web(
    request: WebCheckinRequest,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token inválido")
        
    user_id = UUID(user_id_str)
    
    # 1. Fetch user
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    if user.tipo != TipoUsuario.STAFF:
        raise HTTPException(status_code=403, detail="Check-in Web permitido apenas para STAFF")
        
    if not user.admin_aprovado:
        raise HTTPException(status_code=403, detail="Usuário não aprovado pelo administrador")

    # TODO: Register check-in logically (using CheckinUseCase but bypassing geofence logic, 
    # or just saving it here). Since STAFF doesn't have strict time/geofence constraints, 
    # we can just register the check-in immediately.
    
    from datetime import datetime, timezone
    from app.adapters.persistence.orm_models import Checkin as CheckinModel
    from app.domain.enums import StatusCheckin
    
    # For STAFF we don't have Turno constraints strictly, but we need a 'turno_referencia'.
    # We can use the current date as reference.
    now = datetime.now(timezone.utc)
    turno_ref = now.strftime("%Y-%m-%d_STAFF")
    
    checkin = CheckinModel(
        user_id=user.id,
        # We need a device_id. For web, maybe they have a registered web device?
        # Let's see if they have any device
        device_id=user.devices[0].id if getattr(user, 'devices', None) and user.devices else None, 
        hora_checkin=now,
        ip_publico=f"{request.lat},{request.lng}", # reuse ip_publico for coordinates for now or let it null
        status=StatusCheckin.PRESENTE,
        turno_referencia=turno_ref
    )
    
    # Wait, device_id is required (nullable=False)
    if not checkin.device_id:
        # fetch their device
        dev_res = await db.execute(select(DeviceModel).where(DeviceModel.user_id == user.id))
        dev = dev_res.scalars().first()
        if not dev:
            raise HTTPException(status_code=403, detail="Dispositivo não registrado")
        checkin.device_id = dev.id
        
    db.add(checkin)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        # might be duplicate (unique constraint on user_id, turno_referencia)
        if "uq_checkin_user_turno" in str(e):
            raise HTTPException(status_code=409, detail="Você já bateu o ponto hoje")
        raise
        
    return {"status": "sucesso", "mensagem": "Ponto registrado (STAFF Web)"}
"""

if "class WebCheckinRequest" not in content:
    content = content.replace("from app.domain.enums import TipoUsuario", "from app.domain.enums import TipoUsuario, StatusCheckin")
    content += endpoint

with open("backend/app/api/v1/router_checkin.py", "w") as f:
    f.write(content)
