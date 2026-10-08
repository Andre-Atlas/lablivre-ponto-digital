import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from app.main import app
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import User as UserModel, Device as DeviceModel
from app.domain.enums import TipoUsuario, RoleAdmin
from app.adapters.auth.jwt_handler import create_access_token
from sqlalchemy import text


@pytest.fixture
async def setup_aluno_andrealvesacioli():
    user_id = uuid.uuid4()
    device_id = uuid.uuid4()

    async with async_session_maker() as session:
        # Clear tables just in case
        await session.execute(text("DELETE FROM checkins"))
        await session.execute(text("DELETE FROM devices"))
        await session.execute(text("DELETE FROM users"))

        # Creating exact user requested
        u_aluno = UserModel(
            id=user_id,
            email="andrealvesacioli@gmail.com",
            nome="Andre Alves Acioli",
            tipo=TipoUsuario.ALUNO,
            role=RoleAdmin.NONE,
            turma_ou_equipe="Turma 1",
            oauth_provider="g",
            oauth_sub="12345",
            ativo=True,
            admin_aprovado=True,
        )

        d_aluno = DeviceModel(
            id=device_id,
            user_id=user_id,
            mac_address="00:11:22:33:44:55",
            os_type="win",
            hostname="PC-ANDRE",
            serial_number="XYZ",
            principal=True,
        )

        session.add_all([u_aluno, d_aluno])
        await session.commit()

    token = create_access_token(data={"sub": str(user_id), "tipo": TipoUsuario.ALUNO.value})
    yield {"token": token, "device_id": str(device_id)}


@pytest.mark.asyncio
async def test_andrealvesacioli_checkin_weekend_or_bad_coords(setup_aluno_andrealvesacioli):
    data = setup_aluno_andrealvesacioli
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"device_mac": "00:11:22:33:44:55", "ssid": "My_Wifi", "bssids": ["WRONG_BSSID"]}

        res = await ac.post(
            "/api/v1/checkin/", json=payload, headers={"Authorization": f"Bearer {data['token']}"}
        )

        # Since the user requested "deve dar erro", we expect 403 or 400
        assert res.status_code in [400, 403]

        json_resp = res.json()
        assert "detail" in json_resp
        # Could be Out of Geofence or No Active Shift (Weekend)
        assert (
            "turno" in json_resp["detail"].lower()
            or "distância" in json_resp["detail"].lower()
            or "bssid" in json_resp["detail"].lower()
        )
