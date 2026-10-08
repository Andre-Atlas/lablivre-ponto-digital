
with open("backend/app/api/v1/router_admin.py") as f:
    content = f.read()

# First add the Pydantic schema
schema = """
class JustificarRequest(BaseModel):
    data: str  # YYYY-MM-DD
    turno: str # MANHA or TARDE
"""
if "class JustificarRequest" not in content:
    content = content.replace(
        "class RoleUpdateRequest(BaseModel):", schema + "\nclass RoleUpdateRequest(BaseModel):"
    )

endpoint = """
@router.post("/usuarios/{user_id}/justificar")
async def justificar_falta(
    user_id: UUID,
    request: JustificarRequest,
    current_admin: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Verify user exists
    user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    turno_ref = f"{request.data}_{request.turno}"
    
    # Check if checkin already exists
    existing = await db.execute(select(CheckInModel).where(
        CheckInModel.user_id == user_id,
        CheckInModel.turno_referencia == turno_ref
    ))
    checkin = existing.scalars().first()
    
    if checkin:
        # Update existing
        checkin.status = StatusCheckin.JUSTIFICADO
    else:
        # Create new dummy checkin for the justification
        # Get the user's first device or create a mock web device
        # Note: device_id is required. We'll use a dummy ID or the admin's device?
        # A checkin needs a device. Let's create a generic "Admin Justification" device if none exists.
        
        dev_result = await db.execute(select(DeviceModel).where(DeviceModel.user_id == user_id))
        dev = dev_result.scalars().first()
        if not dev:
            import uuid
            dev = DeviceModel(
                id=uuid.uuid4(),
                user_id=user_id,
                mac_address="JUSTIFICADO_WEB",
                os_type="web",
                hostname="Painel_Admin",
                serial_number="N/A",
                principal=True
            )
            db.add(dev)
            await db.flush()
            
        from datetime import datetime, timezone
        
        checkin = CheckInModel(
            user_id=user_id,
            device_id=dev.id,
            hora_checkin=datetime.now(timezone.utc), # Audit time
            status=StatusCheckin.JUSTIFICADO,
            turno_referencia=turno_ref,
            ip_publico="0.0.0.0"
        )
        db.add(checkin)
        
    await db.commit()
    return {"status": "sucesso", "mensagem": "Falta/Atraso justificado com sucesso."}
"""

if '@router.post("/usuarios/{user_id}/justificar")' not in content:
    content += "\n" + endpoint

with open("backend/app/api/v1/router_admin.py", "w") as f:
    f.write(content)
