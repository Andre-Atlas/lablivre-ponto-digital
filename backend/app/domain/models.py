from __future__ import annotations

"""Entidades de domínio puras do Ponto Digital.

Todas as entidades são dataclasses sem dependência de ORM ou frameworks.
Inclui funções de negócio para identificação de turnos e cálculo de status.
"""

from dataclasses import dataclass, field
from datetime import datetime, time, date, timedelta
from uuid import UUID
from typing import Optional

from .enums import TipoUsuario, StatusCheckin, DiaSemana, Turno, RoleAdmin


# ──────────────────────────────────────────────
# Entidades de Domínio
# ──────────────────────────────────────────────


@dataclass
class User:
    """Usuário do sistema (aluno ou membro da equipe)."""

    id: UUID
    email: str
    nome: str
    tipo: TipoUsuario
    turma_ou_equipe: str
    oauth_provider: str
    oauth_sub: str
    ativo: bool
    admin_aprovado: bool
    criado_em: datetime
    atualizado_em: datetime
    role: RoleAdmin = field(default=RoleAdmin.NONE)
    patrimonio: Optional[str] = None


@dataclass
class Device:
    """Dispositivo vinculado a um usuário."""

    id: UUID
    user_id: UUID
    mac_address: str
    os_type: str
    principal: bool
    registrado_em: datetime
    serial_number: Optional[str] = None
    hostname: Optional[str] = None


@dataclass
class CheckIn:
    """Registro de ponto (check-in) de um usuário."""

    id: UUID
    user_id: UUID
    device_id: UUID
    hora_checkin: datetime
    bssids: list[str]
    status: StatusCheckin
    turno_referencia: str
    exportado_sheets: bool
    criado_em: datetime
    ip_publico: Optional[str] = None
    ssid: Optional[str] = None


@dataclass
class CheckInDuplicata:
    """Registro de tentativa duplicada de check-in (para auditoria)."""

    id: UUID
    checkin_original_id: UUID
    user_id: UUID
    device_id: UUID
    hora_tentativa: datetime
    motivo: str
    criado_em: datetime
    ip_publico: Optional[str] = None


@dataclass
class Config:
    """Configuração dinâmica do sistema (chave-valor)."""

    id: UUID
    chave: str
    valor: str
    atualizado_em: datetime
    role: RoleAdmin = field(default=RoleAdmin.NONE)
    atualizado_por: Optional[UUID] = None


# ──────────────────────────────────────────────
# Configuração de Turnos
# ──────────────────────────────────────────────


@dataclass(frozen=True)
class TurnoConfig:
    """Configuração de um turno específico para uma turma."""

    turma: str
    dia: DiaSemana
    inicio: time
    fim: time
    turno: Turno


# Definição fixa dos turnos das turmas de alunos
TURNOS_ALUNOS: list[TurnoConfig] = [
    # Turma 1: Seg/Qua 08:00-12:00 + 14:00-18:00; Sex 08:00-12:00
    TurnoConfig(turma="Turma 1", dia=DiaSemana.SEG, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA),
    TurnoConfig(turma="Turma 1", dia=DiaSemana.SEG, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE),
    TurnoConfig(turma="Turma 1", dia=DiaSemana.QUA, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA),
    TurnoConfig(turma="Turma 1", dia=DiaSemana.QUA, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE),
    TurnoConfig(turma="Turma 1", dia=DiaSemana.SEX, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA),
    # Turma 2: Ter/Qui 08:00-12:00 + 14:00-18:00; Sex 14:00-18:00
    TurnoConfig(turma="Turma 2", dia=DiaSemana.TER, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA),
    TurnoConfig(turma="Turma 2", dia=DiaSemana.TER, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE),
    TurnoConfig(turma="Turma 2", dia=DiaSemana.QUI, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA),
    TurnoConfig(turma="Turma 2", dia=DiaSemana.QUI, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE),
    TurnoConfig(turma="Turma 2", dia=DiaSemana.SEX, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE),
]

# Mapeamento de weekday() do Python para DiaSemana
_DIA_SEMANA_MAP: dict[int, DiaSemana] = {
    0: DiaSemana.SEG,
    1: DiaSemana.TER,
    2: DiaSemana.QUA,
    3: DiaSemana.QUI,
    4: DiaSemana.SEX,
}


# ──────────────────────────────────────────────
# Funções de Negócio
# ──────────────────────────────────────────────


def identificar_turno(turma_ou_equipe: str, timestamp: datetime) -> TurnoConfig | None:
    """Identifica o turno ativo para uma turma/equipe em um dado momento.

    Args:
        turma_ou_equipe: Nome da turma ou equipe do usuário.
        timestamp: Data/hora para verificar qual turno está ativo.

    Returns:
        TurnoConfig do turno ativo, ou None se não houver turno.
    """
    # Fim de semana → sem turno
    if timestamp.weekday() > 4:
        return None

    dia_atual = _DIA_SEMANA_MAP.get(timestamp.weekday())
    if dia_atual is None:
        return None

    hora_atual = timestamp.time()

    for config in TURNOS_ALUNOS:
        if config.turma == turma_ou_equipe and config.dia == dia_atual:
            if config.inicio <= hora_atual <= config.fim:
                return config

    return None


def calcular_status(
    hora_checkin: datetime,
    turno_inicio: time,
    carencia_minutos: int,
) -> StatusCheckin:
    """Calcula o status do check-in com base na carência configurada.

    Args:
        hora_checkin: Momento do check-in.
        turno_inicio: Horário de início do turno.
        carencia_minutos: Minutos de tolerância configurados pelo admin.

    Returns:
        PRESENTE se dentro da carência, ATRASADO caso contrário.
    """
    checkin_date = hora_checkin.date()
    inicio_datetime = datetime.combine(checkin_date, turno_inicio)

    diferenca = hora_checkin - inicio_datetime
    minutos_atraso = diferenca.total_seconds() / 60.0

    if minutos_atraso <= carencia_minutos:
        return StatusCheckin.PRESENTE
    return StatusCheckin.ATRASADO
