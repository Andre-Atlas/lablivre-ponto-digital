with open("backend/tests/integration/test_excel_export.py", "r") as f:
    content = f.read()
    
# We need to import DeviceModel and add it
content = content.replace(
    "from app.adapters.persistence.orm_models import User as UserModel, Checkin as CheckInModel",
    "from app.adapters.persistence.orm_models import User as UserModel, Checkin as CheckInModel, Device as DeviceModel"
)

new_checkin = """
        dev_id = uuid.uuid4()
        d1 = DeviceModel(id=dev_id, user_id=staff_id, mac_address="mac1", os_type="win", hostname="host1", serial_number="sn1")
        session.add(d1)
        await session.flush()
        
        c1 = CheckInModel(user_id=staff_id, device_id=dev_id, hora_checkin=datetime.now(timezone.utc), ip_publico="1.1.1.1", status=StatusCheckin.PRESENTE, turno_referencia="STAFF_MANHA")
        c2 = CheckInModel(user_id=aluno_id, device_id=dev_id, hora_checkin=datetime.now(timezone.utc), ip_publico="1.1.1.2", status=StatusCheckin.ATRASADO, turno_referencia="ALUNO_MANHA")
"""

import re
pattern = re.compile(r'c1 = CheckInModel.*?c2 = CheckInModel.*?turno_referencia="ALUNO_MANHA"\)', re.DOTALL)
content = pattern.sub(new_checkin.strip(), content)

with open("backend/tests/integration/test_excel_export.py", "w") as f:
    f.write(content)
