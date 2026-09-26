import pytest
from httpx import AsyncClient, ASGITransport
import uuid
from app.main import app
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import User as UserModel
from app.domain.enums import TipoUsuario, RoleAdmin
from app.adapters.auth.jwt_handler import create_access_token
from sqlalchemy import text

@pytest.fixture
async def setup_users():
    super_admin_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    staff_id = uuid.uuid4()
    aluno_id = uuid.uuid4()
    
    async with async_session_maker() as session:
        # Mock users
        u1 = UserModel(id=super_admin_id, email="super@test.com", nome="Super", tipo=TipoUsuario.STAFF, role=RoleAdmin.SUPER_ADMIN, turma_ou_equipe="STAFF", oauth_provider="google", oauth_sub="1", ativo=True, admin_aprovado=True)
        u2 = UserModel(id=admin_id, email="admin@test.com", nome="Admin", tipo=TipoUsuario.STAFF, role=RoleAdmin.ADMIN, turma_ou_equipe="STAFF", oauth_provider="google", oauth_sub="2", ativo=True, admin_aprovado=True)
        u3 = UserModel(id=staff_id, email="staff@test.com", nome="Staff", tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma_ou_equipe="STAFF", oauth_provider="google", oauth_sub="3", ativo=True, admin_aprovado=True)
        u4 = UserModel(id=aluno_id, email="aluno@test.com", nome="Aluno", tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma_ou_equipe="Turma", oauth_provider="google", oauth_sub="4", ativo=True, admin_aprovado=True)
        
        session.add_all([u1, u2, u3, u4])
        await session.commit()
    
    yield {
        "super": {"id": str(super_admin_id), "token": create_access_token(data={"sub": str(super_admin_id)})},
        "admin": {"id": str(admin_id), "token": create_access_token(data={"sub": str(admin_id)})},
        "staff": {"id": str(staff_id), "token": create_access_token(data={"sub": str(staff_id)})},
        "aluno": {"id": str(aluno_id), "token": create_access_token(data={"sub": str(aluno_id)})},
    }
    
    async with async_session_maker() as session:
        await session.execute(text("DELETE FROM users WHERE email IN ('super@test.com', 'admin@test.com', 'staff@test.com', 'aluno@test.com')"))
        await session.commit()

@pytest.mark.asyncio
async def test_roles_access(setup_users):
    users = setup_users
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Staff (role=NONE) trying to access /api/v1/admin/usuarios -> Should fail (403)
        res_staff = await ac.get("/api/v1/admin/usuarios", headers={"Authorization": f"Bearer {users['staff']['token']}"})
        assert res_staff.status_code == 403
        
        # 2. Admin trying to access /api/v1/admin/usuarios -> Should succeed (200)
        res_admin = await ac.get("/api/v1/admin/usuarios", headers={"Authorization": f"Bearer {users['admin']['token']}"})
        assert res_admin.status_code == 200
        
        # 3. Super Admin trying to access /api/v1/admin/usuarios -> Should succeed (200)
        res_super = await ac.get("/api/v1/admin/usuarios", headers={"Authorization": f"Bearer {users['super']['token']}"})
        assert res_super.status_code == 200
        
        # 4. Admin trying to promote user to Super Admin -> Should fail (403)
        res_admin_promote = await ac.post(f"/api/v1/admin/usuarios/{users['staff']['id']}/role", json={"role": "SUPER_ADMIN"}, headers={"Authorization": f"Bearer {users['admin']['token']}"})
        assert res_admin_promote.status_code == 403
        
        # 5. Super Admin trying to promote user to Admin -> Should succeed (200)
        res_super_promote = await ac.post(f"/api/v1/admin/usuarios/{users['staff']['id']}/role", json={"role": "ADMIN"}, headers={"Authorization": f"Bearer {users['super']['token']}"})
        assert res_super_promote.status_code == 200
