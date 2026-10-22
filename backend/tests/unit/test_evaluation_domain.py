"""Testes unitários do domínio de avaliação semanal de LOs (T003).

Cobrem derivação de semana, pré-preenchimento (último nível por LO) e detecção de regressão.
Não dependem de banco de dados.
"""

import uuid
from datetime import date

from app.domain.models import (
    detectar_regressoes,
    niveis_anteriores,
    nivel_valido,
    semana_atual,
    semana_de,
    semana_no_intervalo,
)


def test_semana_de_conta_a_partir_de_1() -> None:
    inicio = date(2026, 1, 5)  # segunda, semana 1
    assert semana_de(date(2026, 1, 5), inicio) == 1
    assert semana_de(date(2026, 1, 11), inicio) == 1  # mesmo bloco de 7 dias
    assert semana_de(date(2026, 1, 12), inicio) == 2
    assert semana_de(date(2026, 2, 2), inicio) == 5


def test_semana_atual_limita_ao_intervalo() -> None:
    inicio = date(2026, 1, 5)
    assert semana_atual(date(2026, 1, 1), inicio, 12) == 1  # antes do início → 1
    assert semana_atual(date(2026, 1, 12), inicio, 12) == 2
    assert semana_atual(date(2027, 1, 1), inicio, 12) == 12  # depois do fim → num_semanas


def test_semana_no_intervalo() -> None:
    assert semana_no_intervalo(1, 12) is True
    assert semana_no_intervalo(12, 12) is True
    assert semana_no_intervalo(0, 12) is False
    assert semana_no_intervalo(13, 12) is False


def test_nivel_valido() -> None:
    assert all(nivel_valido(n) for n in (1, 2, 3, 4))
    assert not nivel_valido(0)
    assert not nivel_valido(5)


def test_niveis_anteriores_pega_semana_mais_recente_por_lo() -> None:
    lo1, lo2 = uuid.uuid4(), uuid.uuid4()
    rows = [
        (1, lo1, 2),
        (2, lo1, 3),  # mais recente para lo1 (< semana 4)
        (1, lo2, 1),
        (4, lo1, 4),  # ignorado: não é < 4
    ]
    resultado = niveis_anteriores(rows, antes_de_semana=4)
    assert resultado == {lo1: 3, lo2: 1}


def test_niveis_anteriores_vazio_quando_sem_historico() -> None:
    lo1 = uuid.uuid4()
    assert niveis_anteriores([(5, lo1, 3)], antes_de_semana=3) == {}


def test_detectar_regressoes_somente_com_anterior_comparavel() -> None:
    lo1, lo2, lo3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    atuais = {lo1: 2, lo2: 4, lo3: 1}
    anteriores = {lo1: 3, lo2: 2}  # lo3 sem anterior comparável
    regs = detectar_regressoes(atuais, anteriores)
    assert regs == [(lo1, 2, 3)]  # só lo1 caiu; lo2 subiu; lo3 não tem comparação
