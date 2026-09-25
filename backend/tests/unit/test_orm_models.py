import pytest
from app.adapters.persistence.orm_models import (
    User, Device, Checkin, CheckinDuplicata, Config, 
    Admin, IpAllowlist, BssidAllowlist,
    TipoUsuario, StatusCheckin, RoleAdmin
)
import uuid
from datetime import datetime, timezone

def test_user_instantiation():
    """Testa a instanciação do modelo User e seus valores padrão."""
    user = User(
        email="teste@aluno.com",
        nome="Teste Aluno",
        tipo=TipoUsuario.ALUNO,
        turma_ou_equipe="3A",
        oauth_provider="google",
        oauth_sub="sub123"
    )
    assert user.email == "teste@aluno.com"
    assert user.tipo == TipoUsuario.ALUNO

def test_device_instantiation():
    """Testa a criação de uma instância de Device."""
    user_id = uuid.uuid4()
    device = Device(
        user_id=user_id,
        mac_address="00:11:22:33:44:55",
        os_type="macOS"
    )
    assert device.user_id == user_id
    assert device.mac_address == "00:11:22:33:44:55"

def test_checkin_instantiation():
    """Testa a criação de um Checkin e suas relações básicas."""
    user_id = uuid.uuid4()
    device_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    
    checkin = Checkin(
        user_id=user_id,
        device_id=device_id,
        hora_checkin=now,
        status=StatusCheckin.PRESENTE,
        turno_referencia="2026-09-24_MANHA"
    )
    
    assert checkin.turno_referencia == "2026-09-24_MANHA"
    assert checkin.status == StatusCheckin.PRESENTE

def test_admin_instantiation():
    """Testa a instanciação do Admin."""
    admin = Admin(
        email="admin@escola.com",
        nome="Admin Principal",
        role=RoleAdmin.SUPER_ADMIN,
        oauth_provider="google",
        oauth_sub="admin_sub"
    )
    assert admin.role == RoleAdmin.SUPER_ADMIN

def test_config_instantiation():
    """Testa a criação de configurações."""
    config = Config(
        chave="CHECKIN_START_TIME",
        valor="07:00"
    )
    assert config.chave == "CHECKIN_START_TIME"
    assert config.valor == "07:00"
