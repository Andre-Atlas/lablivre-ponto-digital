from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.domain.enums import TipoUsuario

class OnboardingRequest(BaseModel):
    oauth_provider: str
    oauth_token: str
    tipo: TipoUsuario
    turma_ou_equipe: Optional[str] = None
    patrimonio: Optional[str] = None
    device_mac: str
    device_os: str
    device_hostname: Optional[str] = None
    device_serial: Optional[str] = None

class OnboardingResponse(BaseModel):
    status: str
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
