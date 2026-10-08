with open("backend/tests/integration/test_excel_export.py", "r") as f:
    content = f.read()

import re
old_setup = re.search(r'async with async_session_maker\(\) as session:.*?await session\.commit\(\)', content, re.DOTALL).group(0)

new_setup = """async with async_session_maker() as session:
        # Clear tables just in case
        await session.execute(text("DELETE FROM checkins"))
        await session.execute(text("DELETE FROM devices"))
        await session.execute(text("DELETE FROM users"))
        
        u_super = UserModel(id=super_id, email="super@test.com", nome="Super", tipo=TipoUsuario.STAFF, role=RoleAdmin.SUPER_ADMIN, turma_ou_equipe="STAFF", oauth_provider="g", oauth_sub="1", ativo=True, admin_aprovado=True)
        u_staff = UserModel(id=staff_id, email="staff@test.com", nome="Staff", tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma_ou_equipe="STAFF", oauth_provider="g", oauth_sub="2", ativo=True, admin_aprovado=True)
        u_aluno = UserModel(id=aluno_id, email="aluno@test.com", nome="Aluno 1", tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma_ou_equipe="Turma 1", oauth_provider="g", oauth_sub="3", ativo=True, admin_aprovado=True)
        
        dev_id = uuid.uuid4()
        d1 = DeviceModel(id=dev_id, user_id=staff_id, mac_address="mac1", os_type="win", hostname="host1", serial_number="sn1")
        d2 = DeviceModel(id=uuid.uuid4(), user_id=aluno_id, mac_address="mac2", os_type="win", hostname="host2", serial_number="sn2")
        
        c1 = CheckInModel(user_id=staff_id, device_id=dev_id, hora_checkin=datetime.now(timezone.utc), ip_publico="1.1.1.1", status=StatusCheckin.PRESENTE, turno_referencia="STAFF_MANHA")
        c2 = CheckInModel(user_id=aluno_id, device_id=d2.id, hora_checkin=datetime.now(timezone.utc), ip_publico="1.1.1.2", status=StatusCheckin.ATRASADO, turno_referencia="ALUNO_MANHA")

        session.add_all([u_super, u_staff, u_aluno, d1, d2, c1, c2])
        await session.commit()"""

content = content.replace(old_setup, new_setup)
with open("backend/tests/integration/test_excel_export.py", "w") as f:
    f.write(content)
