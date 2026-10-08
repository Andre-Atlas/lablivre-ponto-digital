from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError

from app.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com os dados fornecidos.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Usa um fallback se JWT_EXPIRE_HOURS não estiver definido, embora devesse estar em settings
        expire_hours = getattr(settings, "JWT_EXPIRE_HOURS", 24)
        expire = datetime.now(timezone.utc) + timedelta(hours=expire_hours)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=getattr(settings, "JWT_ALGORITHM", "HS256")
    )
    return encoded_jwt


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica um token JWT e retorna o payload caso seja válido.
    Retorna None se o token for inválido ou estiver expirado.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[getattr(settings, "JWT_ALGORITHM", "HS256")]
        )
        return payload
    except JWTError:
        return None
