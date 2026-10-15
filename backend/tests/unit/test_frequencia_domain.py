"""Testes de domínio da frequência (puros)."""
from app.domain.models import pode_anexar_atestado, status_com_atestado


def test_status_com_atestado():
    assert status_com_atestado(True, "FALTA") == "JUSTIFICADO"
    assert status_com_atestado(False, "FALTA") == "FALTA"
    # Presente nunca vira Justificado, mesmo com flag.
    assert status_com_atestado(True, "PRESENTE") == "PRESENTE"


def test_pode_anexar_atestado():
    assert pode_anexar_atestado("FALTA") is True
    assert pode_anexar_atestado("JUSTIFICADO") is True
    assert pode_anexar_atestado("PRESENTE") is False
