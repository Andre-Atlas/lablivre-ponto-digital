"""Testes unitários do domínio de atestados médicos (T004).

Cobrem a validação de período e a expansão pura de um período em turnos esperados da turma.
Não dependem de banco de dados.
"""

from datetime import date

from app.domain.enums import Turno
from app.domain.models import expandir_turnos_periodo, periodo_valido


def test_periodo_valido_aceita_fim_igual_ou_posterior() -> None:
    assert periodo_valido(date(2026, 10, 5), date(2026, 10, 9)) is True
    assert periodo_valido(date(2026, 10, 5), date(2026, 10, 5)) is True


def test_periodo_valido_rejeita_fim_anterior() -> None:
    assert periodo_valido(date(2026, 10, 9), date(2026, 10, 5)) is False


def test_expandir_turma1_semana_completa() -> None:
    # Turma 1: SEG(MANHA,TARDE), QUA(MANHA,TARDE), SEX(MANHA). 2026-10-05 = segunda-feira.
    shifts = expandir_turnos_periodo("Turma 1", date(2026, 10, 5), date(2026, 10, 9))
    refs = [ref for _, _, ref in shifts]
    assert refs == [
        "2026-10-05_MANHA",
        "2026-10-05_TARDE",
        "2026-10-07_MANHA",
        "2026-10-07_TARDE",
        "2026-10-09_MANHA",
    ]


def test_expandir_um_dia_com_dois_turnos() -> None:
    shifts = expandir_turnos_periodo("Turma 1", date(2026, 10, 5), date(2026, 10, 5))
    turnos = sorted(t for _, t, _ in shifts)
    assert turnos == [Turno.MANHA, Turno.TARDE]


def test_expandir_fim_de_semana_vazio() -> None:
    # 2026-10-10 = sábado, 2026-10-11 = domingo
    assert expandir_turnos_periodo("Turma 1", date(2026, 10, 10), date(2026, 10, 11)) == []


def test_expandir_periodo_invertido_vazio() -> None:
    assert expandir_turnos_periodo("Turma 1", date(2026, 10, 9), date(2026, 10, 5)) == []


def test_expandir_turma_inexistente_vazio() -> None:
    assert expandir_turnos_periodo("Turma Fantasma", date(2026, 10, 5), date(2026, 10, 9)) == []
