import pytest
from datetime import timedelta
from app.adapters.auth.jwt_handler import create_access_token, verify_access_token

def test_create_access_token():
    """Testa se a função de criação gera um JWT em formato string válido."""
    data = {"sub": "user_123", "tipo": "funcionario"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # Verifica estrutura de 3 partes do JWT

def test_verify_access_token_valid():
    """Testa se a verificação funciona para um token válido, recuperando os mesmos dados."""
    data = {"sub": "user_456", "role": "ADMIN"}
    token = create_access_token(data)
    
    payload = verify_access_token(token)
    assert payload is not None
    assert payload.get("sub") == "user_456"
    assert payload.get("role") == "ADMIN"
    assert "exp" in payload

def test_verify_access_token_expired():
    """Testa se a verificação retorna None para um token expirado."""
    data = {"sub": "user_789"}
    # Cria token com delta negativo (já expirado em 1 hora)
    expired_delta = timedelta(hours=-1)
    token = create_access_token(data, expires_delta=expired_delta)
    
    payload = verify_access_token(token)
    assert payload is None
