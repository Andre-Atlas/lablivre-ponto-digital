from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

resp_login = client.post(
    "/api/v1/auth/admin-login", json={"email": "admin@example.com", "password": "admin123"}
)
print("Login:", resp_login.status_code, resp_login.text)
token = resp_login.json()["access_token"]

resp_users = client.get("/api/v1/admin/usuarios", headers={"Authorization": f"Bearer {token}"})
print("Users:", resp_users.status_code, resp_users.text)
