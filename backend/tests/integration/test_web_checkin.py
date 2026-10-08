import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.adapters.auth.jwt_handler import create_access_token
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import Device as DeviceModel
from app.adapters.persistence.orm_models import User as UserModel
from app.domain.enums import TipoUsuario
from app.main import app


@pytest.fixture
async def setup_users():
    staff_id = uuid.uuid4()
    aluno_id = uuid.uuid4()
    device_id = uuid.uuid4()

    async with async_session_maker() as session:
        u1 = UserModel(
            id=staff_id,
            email="staff_web@test.com",
            nome="Staff",
            tipo=TipoUsuario.STAFF,
            turma_ou_equipe="STAFF",
            oauth_provider="google",
            oauth_sub="1",
            ativo=True,
            admin_aprovado=True,
        )
        u2 = UserModel(
            id=aluno_id,
            email="aluno_web@test.com",
            nome="Aluno",
            tipo=TipoUsuario.ALUNO,
            turma_ou_equipe="Turma",
            oauth_provider="google",
            oauth_sub="2",
            ativo=True,
            admin_aprovado=True,
        )
        d1 = DeviceModel(
            id=device_id,
            user_id=staff_id,
            mac_address="web-browser",
            os_type="web",
            hostname="browser",
            serial_number="web",
        )

        session.add_all([u1, u2, d1])
        await session.commit()

    yield {
        "staff_token": create_access_token(data={"sub": str(staff_id)}),
        "aluno_token": create_access_token(data={"sub": str(aluno_id)}),
    }

    async with async_session_maker() as session:
        await session.execute(
            text("DELETE FROM users WHERE email IN ('staff_web@test.com', 'aluno_web@test.com')")
        )
        await session.commit()


@pytest.mark.asyncio
async def test_web_checkin(setup_users):
    users = setup_users
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Aluno trying to use Web Checkin -> Should fail (403)
        payload = {"lat": -23.5, "lng": -46.6}
        res_aluno = await ac.post(
            "/api/v1/checkin/web",
            json=payload,
            headers={"Authorization": f"Bearer {users['aluno_token']}"},
        )
        assert res_aluno.status_code == 403

        # 2. Staff trying to use Web Checkin -> Should succeed (201) (or 400 if weekend, but endpoint works)
        res_staff = await ac.post(
            "/api/v1/checkin/web",
            json=payload,
            headers={"Authorization": f"Bearer {users['staff_token']}"},
        )
        print(res_staff.json())
        assert res_staff.status_code in [
            201,
            400,
        ]  # 400 if weekend/out of shift, but not 403 or 404
