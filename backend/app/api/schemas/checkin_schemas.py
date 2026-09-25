from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CheckinRequest(BaseModel):
    device_mac: str
    ssid: Optional[str] = None
    bssids: List[str]

class CheckinResponse(BaseModel):
    status_checkin: str
    turno: str
    mensagem: str
    hora_registrada: datetime
