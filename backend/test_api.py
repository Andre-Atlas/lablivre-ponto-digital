import asyncio
import random
import uuid

from app.adapters.auth.jwt_handler import create_access_token
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import Device, User
from app.domain.enums import TipoUsuario


async def setup_test_data():
    user_id = uuid.uuid4()
    device_id = uuid.uuid4()
    mac = f"00:11:22:33:44:{random.randint(10, 99)}"
    rand_email = f"aluno.teste.{random.randint(1000, 9999)}@escola.com"

    async with async_session_maker() as session:
        # Create User - TURMA 2 (Quinta-feira tem aula de manhã!)
        user = User(
            id=user_id,
            email=rand_email,
            nome="Aluno Turma 2",
            tipo=TipoUsuario.ALUNO,
            turma_ou_equipe="Turma 2",
            oauth_provider="google",
            oauth_sub="google_sub_123",
            patrimonio="PAT-12345",
            admin_aprovado=True,
            ativo=True,
        )
        session.add(user)

        # Create Device
        device = Device(id=device_id, user_id=user_id, mac_address=mac, os_type="macOS")
        session.add(device)
        await session.commit()

    return user_id, mac


async def run_tests():
    print("=== Configurando dados de teste ===")
    user_id, mac = await setup_test_data()
    print(f"Usuário Turma 2 criado: {user_id}")

    token = create_access_token({"sub": str(user_id), "tipo": "ALUNO"})

    payload = {"device_mac": mac, "ssid": "WIFI_ESCOLA", "bssids": ["aa:bb:cc:dd:ee:ff"]}
    headers = {"Authorization": f"Bearer {token}"}

    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        print("\n=== Check-in Turma 2 (Quinta-feira) ===")
        response = test_client.post("/api/v1/checkin/", json=payload, headers=headers)
        print(f"Status HTTP: {response.status_code}")
        print("Resposta:", response.json())

        print("\n=== Testando Duplicata ===")
        response_dup = test_client.post("/api/v1/checkin/", json=payload, headers=headers)
        print(f"Status HTTP: {response_dup.status_code}")
        print("Resposta:", response_dup.json())


if __name__ == "__main__":
    asyncio.run(run_tests())
