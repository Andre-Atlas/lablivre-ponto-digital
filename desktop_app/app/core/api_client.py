import httpx
from .config import settings
from .state import app_state

class ApiClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL

    @property
    def headers(self):
        h = {"Content-Type": "application/json"}
        if app_state.token:
            h["Authorization"] = f"Bearer {app_state.token}"
        return h

    def get(self, endpoint: str):
        with httpx.Client(timeout=30.0) as client:
            return client.get(f"{self.base_url}{endpoint}", headers=self.headers)

    def post(self, endpoint: str, json: dict = None):
        with httpx.Client(timeout=30.0) as client:
            return client.post(f"{self.base_url}{endpoint}", json=json, headers=self.headers)

api = ApiClient()
