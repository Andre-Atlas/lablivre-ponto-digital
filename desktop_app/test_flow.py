from app.core.api_client import api
from app.utils.network import get_current_mac
real_mac = get_current_mac()
print("MAC:", real_mac)
try:
    resp = api.post("/api/v1/auth/onboarding", json={
        "oauth_token": "fake_token_for_test",
        "oauth_provider": "google",
        "tipo": "ALUNO",
        "turma_ou_equipe": "Turma 2",
        "patrimonio": "MAC-12345",
        "device_mac": real_mac,
        "device_os": "macOS"
    })
    print("Status:", resp.status_code)
    print("Response:", resp.text)
except Exception as e:
    print("Exception:", e)
