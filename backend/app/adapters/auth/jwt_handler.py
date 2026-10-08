from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import JWTError, jwt

from app.config import settings


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Cria um token JWT com os dados fornecidos.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        # Usa um fallback se JWT_EXPIRE_HOURS não estiver definido, embora devesse estar em settings
        expire_hours = getattr(settings, "JWT_EXPIRE_HOURS", 24)
        expire = datetime.now(UTC) + timedelta(hours=expire_hours)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=getattr(settings, "JWT_ALGORITHM", "HS256")
    )
    return str(encoded_jwt)


def verify_access_token(token: str) -> dict[str, Any] | None:
    """
    Verifica um token JWT e retorna o payload caso seja válido.
    Retorna None se o token for inválido ou estiver expirado.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[getattr(settings, "JWT_ALGORITHM", "HS256")]
        )
        return cast(dict[str, Any], payload)
    except JWTError:
        return None
