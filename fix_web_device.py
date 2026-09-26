with open("backend/app/api/v1/router_checkin.py", "r") as f:
    content = f.read()

old = """
    if not checkin.device_id:
        # fetch their device
        dev_res = await db.execute(select(DeviceModel).where(DeviceModel.user_id == user.id))
        dev = dev_res.scalars().first()
        if not dev:
            raise HTTPException(status_code=403, detail="Dispositivo não registrado")
        checkin.device_id = dev.id
"""

new = """
    if not checkin.device_id:
        # fetch their device
        dev_res = await db.execute(select(DeviceModel).where(DeviceModel.user_id == user.id))
        dev = dev_res.scalars().first()
        if not dev:
            # Auto-register a Web Device for STAFF
            import uuid
            new_dev = DeviceModel(id=uuid.uuid4(), user_id=user.id, mac_address="web-browser-" + str(uuid.uuid4())[:8], os_type="web", hostname="dashboard", serial_number="web")
            db.add(new_dev)
            await db.commit() # commit to get id
            checkin.device_id = new_dev.id
        else:
            checkin.device_id = dev.id
"""

content = content.replace(old, new)
with open("backend/app/api/v1/router_checkin.py", "w") as f:
    f.write(content)
