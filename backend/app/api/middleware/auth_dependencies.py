from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any

from app.adapters.auth.jwt_handler import verify_access_token

# URL de autenticação placeholder para o Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Dependência que recupera e valida o usuário atual a partir do token JWT.
    """
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_admin(payload: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependência que garante que o usuário atual é um administrador, verificando a claim 'role'.
    """
    # Verifica a role
    role = payload.get("role")
    if role not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - Requer privilégios de administrador",
        )
    return payload
