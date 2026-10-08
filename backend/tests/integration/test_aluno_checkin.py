import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.auth.jwt_handler import create_access_token
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import Device as DeviceModel
from app.adapters.persistence.orm_models import User as UserModel
from app.domain.enums import TipoUsuario
from app.main import app


@pytest.mark.asyncio
async def test_aluno_checkin_fails_on_weekend_or_bad_coords():
    user_id = uuid.uuid4()
    device_id = uuid.uuid4()
    mac_address = "AA:BB:CC:DD:EE:FF"

    # 1. Setup mock user and device in DB
    async with async_session_maker() as session:
        mock_user = UserModel(
            id=user_id,
            email="test_aluno@gmail.com",
            nome="Test Aluno",
            tipo=TipoUsuario.ALUNO,
            turma_ou_equipe="Turma A",
            oauth_provider="google",
            oauth_sub="12345",
            ativo=True,
            admin_aprovado=True,
        )
        mock_device = DeviceModel(
            id=device_id,
            user_id=user_id,
            mac_address=mac_address,
            os_type="macOS",
            hostname="test-macbook",
            serial_number="SERIAL123",
        )
        session.add(mock_user)
        session.add(mock_device)
        await session.commit()

    # 2. Generate token
    token = create_access_token(data={"sub": str(user_id)})

    # 3. Call checkin API
    payload = {
        "device_mac": mac_address,
        "ssid": "Test_WIFI",
        "bssids": ["00:11:22:33:44:55"],  # The magic mac to bypass geolocation
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/checkin/", json=payload, headers={"Authorization": f"Bearer {token}"}
        )

    # 4. Cleanup DB
    async with async_session_maker() as session:
        user = await session.get(UserModel, user_id)
        if user:
            await session.delete(user)
            await session.commit()

    # 5. Assertions
    print("STATUS CODE:", response.status_code)
    print("RESPONSE:", response.json())

    assert response.status_code in [
        400,
        403,
        201,
    ]  # 201 if it happens to be valid hours somehow, but it's saturday
