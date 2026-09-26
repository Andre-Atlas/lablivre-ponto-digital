with open("backend/app/api/v1/router_checkin.py", "r") as f:
    content = f.read()

content = content.replace("device_id=user.devices[0].id if getattr(user, 'devices', None) and user.devices else None,", "device_id=None,")

with open("backend/app/api/v1/router_checkin.py", "w") as f:
    f.write(content)
