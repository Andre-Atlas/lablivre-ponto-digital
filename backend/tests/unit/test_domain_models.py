from datetime import datetime, time
from uuid import uuid4

from app.domain.enums import DiaSemana, StatusCheckin, TipoUsuario, Turno
from app.domain.models import (
    TURNOS_ALUNOS,
    User,
    calcular_status,
    identificar_turno,
)


def test_turnos_alunos_corretude():
    assert len(TURNOS_ALUNOS) == 10

    # Verifica Turma 1
    t1_seg_manha = next(
        t
        for t in TURNOS_ALUNOS
        if t.turma == "Turma 1" and t.dia == DiaSemana.SEG and t.turno == Turno.MANHA
    )
    assert t1_seg_manha.inicio == time(8, 0)
    assert t1_seg_manha.fim == time(12, 0)

    # Verifica Turma 2 sexta
    t2_sex_tarde = next(t for t in TURNOS_ALUNOS if t.turma == "Turma 2" and t.dia == DiaSemana.SEX)
    assert t2_sex_tarde.inicio == time(14, 0)
    assert t2_sex_tarde.fim == time(18, 0)


def test_identificar_turno_turma1():
    # Segunda 10:00 - MANHA
    dt1 = datetime(2023, 10, 2, 10, 0)  # 02/10/2023 é segunda-feira
    turno_seg = identificar_turno("Turma 1", dt1)
    assert turno_seg is not None
    assert turno_seg.turno == Turno.MANHA

    # Sexta 09:00 - MANHA
    dt2 = datetime(2023, 10, 6, 9, 0)  # 06/10/2023 é sexta-feira
    turno_sex = identificar_turno("Turma 1", dt2)
    assert turno_sex is not None
    assert turno_sex.turno == Turno.MANHA


def test_identificar_turno_turma2():
    # Terça 15:00 - TARDE
    dt1 = datetime(2023, 10, 3, 15, 0)
    turno = identificar_turno("Turma 2", dt1)
    assert turno is not None
    assert turno.turno == Turno.TARDE


def test_identificar_turno_dia_errado():
    # Turma 2 na Segunda
    dt = datetime(2023, 10, 2, 10, 0)
    turno = identificar_turno("Turma 2", dt)
    assert turno is None


def test_calcular_status_presente():
    hora_checkin = datetime(2023, 10, 2, 8, 10)
    turno_inicio = time(8, 0)
    status = calcular_status(hora_checkin, turno_inicio, carencia_minutos=15)
    assert status == StatusCheckin.PRESENTE


def test_calcular_status_atrasado():
    hora_checkin = datetime(2023, 10, 2, 8, 20)
    turno_inicio = time(8, 0)
    status = calcular_status(hora_checkin, turno_inicio, carencia_minutos=15)
    assert status == StatusCheckin.ATRASADO


def test_calcular_status_na_borda():
    hora_checkin = datetime(2023, 10, 2, 8, 15)
    turno_inicio = time(8, 0)
    status = calcular_status(hora_checkin, turno_inicio, carencia_minutos=15)
    assert status == StatusCheckin.PRESENTE


def test_criacao_entidades():
    uid = uuid4()
    now = datetime.now()
    user = User(
        id=uid,
        email="test@test.com",
        nome="Teste",
        tipo=TipoUsuario.ALUNO,
        turma_ou_equipe="Turma 1",
        oauth_provider="google",
        oauth_sub="123",
        ativo=True,
        admin_aprovado=True,
        criado_em=now,
        atualizado_em=now,
    )
    assert user.id == uid
    assert user.tipo == TipoUsuario.ALUNO
