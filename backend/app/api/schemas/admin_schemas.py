from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.domain.enums import TipoUsuario

class UserAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    nome: str
    tipo: TipoUsuario
    role: Optional[str] = None
    turma_ou_equipe: str
    patrimonio: Optional[str] = None
    ativo: bool
    admin_aprovado: bool
    criado_em: datetime

class DeviceAdminResponse(BaseModel):
    id: UUID
    user_id: UUID
    mac_address: str
    os_type: str
    hostname: Optional[str] = None
    principal: bool
    registrado_em: datetime

class CheckinAdminResponse(BaseModel):
    id: UUID
    user_id: UUID
    device_id: UUID
    hora_checkin: datetime
    status: str
    turno_referencia: str
    exportado_sheets: bool
