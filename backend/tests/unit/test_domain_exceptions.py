from datetime import datetime
from uuid import uuid4

import pytest

from app.domain.exceptions import (
    DomainError,
    DuplicataError,
    ForaDoRaioError,
    ForaTurnoError,
    PatrimonioObrigatorioError,
)


def test_excecoes_base():
    with pytest.raises(DomainError):
        raise ForaTurnoError("Erro de turno")


def test_fora_do_raio_error():
    err = ForaDoRaioError(150.5)
    assert err.distancia_metros == 150.5
    assert "150.50m" in str(err)


def test_duplicata_error():
    uid = uuid4()
    agora = datetime.now()
    err = DuplicataError(checkin_original_id=uid, hora_original=agora)

    assert err.checkin_original_id == uid
    assert err.hora_original == agora
    assert str(uid) in str(err)


def test_patrimonio_obrigatorio_error():
    with pytest.raises(DomainError):
        raise PatrimonioObrigatorioError("Patrimônio é necessário.")
