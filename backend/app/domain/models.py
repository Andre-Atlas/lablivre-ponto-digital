from __future__ import annotations

"""Entidades de domínio puras do Ponto Digital.

Todas as entidades são dataclasses sem dependência de ORM ou frameworks.
Inclui funções de negócio para identificação de turnos e cálculo de status.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from uuid import UUID

from .enums import (
    CertificateStatus,
    DiaSemana,
    RoleAdmin,
    StatusCheckin,
    TipoUsuario,
    Turno,
)

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
    patrimonio: str | None = None


@dataclass
class Device:
    """Dispositivo vinculado a um usuário."""

    id: UUID
    user_id: UUID
    mac_address: str
    os_type: str
    principal: bool
    registrado_em: datetime
    serial_number: str | None = None
    hostname: str | None = None


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
    ip_publico: str | None = None
    ssid: str | None = None


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
    ip_publico: str | None = None


@dataclass
class MedicalCertificate:
    """Atestado médico registrado por um admin para um aluno.

    Um atestado cobre um período contíguo e justifica (via CertificateDay) os turnos
    esperados nesse período em que o aluno não possui check-in presente/atrasado real.
    """

    id: UUID
    user_id: UUID
    periodo_inicio: date
    periodo_fim: date
    documento: bytes
    documento_filename: str
    documento_content_type: str
    documento_tamanho: int
    status: CertificateStatus
    criado_em: datetime
    observacao: str | None = None
    registrado_por: UUID | None = None
    revogado_por: UUID | None = None
    motivo_revogacao: str | None = None
    revogado_em: datetime | None = None


@dataclass
class CertificateDay:
    """Vínculo persistente entre um atestado e um turno justificado do aluno."""

    id: UUID
    certificate_id: UUID
    user_id: UUID
    data: date
    turno: str
    turno_referencia: str
    ativo: bool
    criado_em: datetime


@dataclass
class Config:
    """Configuração dinâmica do sistema (chave-valor)."""

    id: UUID
    chave: str
    valor: str
    atualizado_em: datetime
    role: RoleAdmin = field(default=RoleAdmin.NONE)
    atualizado_por: UUID | None = None


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
    TurnoConfig(
        turma="Turma 1", dia=DiaSemana.SEG, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA
    ),
    TurnoConfig(
        turma="Turma 1", dia=DiaSemana.SEG, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE
    ),
    TurnoConfig(
        turma="Turma 1", dia=DiaSemana.QUA, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA
    ),
    TurnoConfig(
        turma="Turma 1", dia=DiaSemana.QUA, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE
    ),
    TurnoConfig(
        turma="Turma 1", dia=DiaSemana.SEX, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA
    ),
    # Turma 2: Ter/Qui 08:00-12:00 + 14:00-18:00; Sex 14:00-18:00
    TurnoConfig(
        turma="Turma 2", dia=DiaSemana.TER, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA
    ),
    TurnoConfig(
        turma="Turma 2", dia=DiaSemana.TER, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE
    ),
    TurnoConfig(
        turma="Turma 2", dia=DiaSemana.QUI, inicio=time(8, 0), fim=time(12, 0), turno=Turno.MANHA
    ),
    TurnoConfig(
        turma="Turma 2", dia=DiaSemana.QUI, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE
    ),
    TurnoConfig(
        turma="Turma 2", dia=DiaSemana.SEX, inicio=time(14, 0), fim=time(18, 0), turno=Turno.TARDE
    ),
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


# ──────────────────────────────────────────────
# Avaliação Semanal de Learning Outcomes (LOs)
# ──────────────────────────────────────────────

NIVEL_MIN = 1
NIVEL_MAX = 4
NUM_SEMANAS_PADRAO = 12

# Chaves usadas na tabela `config` para a configuração do programa de avaliação.
CFG_DATA_INICIO = "lo_eval_data_inicio"
CFG_NUM_SEMANAS = "lo_eval_num_semanas"


@dataclass
class LearningOutcome:
    """Objetivo de aprendizagem (LO) do catálogo."""

    id: UUID
    numero: int
    nome: str
    ativo: bool
    ordem: int
    criado_em: datetime
    atualizado_em: datetime
    descricao: str | None = None


@dataclass
class EvaluationLevel:
    """Nível (1–4) atribuído a um LO dentro de uma avaliação semanal."""

    id: UUID
    evaluation_id: UUID
    lo_id: UUID
    nivel: int
    atualizado_em: datetime
    mentor_id: UUID | None = None


@dataclass
class EvaluationComment:
    """Comentário de um mentor em uma avaliação semanal."""

    id: UUID
    evaluation_id: UUID
    mentor_nome: str
    texto: str
    atualizado_em: datetime
    mentor_id: UUID | None = None


@dataclass
class WeeklyEvaluation:
    """Avaliação de um aluno em uma semana do programa (níveis por LO + comentários)."""

    id: UUID
    user_id: UUID
    semana: int
    turma: str
    criado_em: datetime
    atualizado_em: datetime
    niveis: list[EvaluationLevel] = field(default_factory=list)
    comentarios: list[EvaluationComment] = field(default_factory=list)


# ──────────────────────────────────────────────
# Funções de Negócio — Avaliação de LOs
# ──────────────────────────────────────────────


def nivel_valido(nivel: int) -> bool:
    """Valida que o nível está no intervalo permitido (1–4)."""
    return NIVEL_MIN <= nivel <= NIVEL_MAX


def semana_de(data_ref: date, data_inicio: date) -> int:
    """Índice de semana (≥ 1) de uma data em relação ao início do programa (semana 1)."""
    return ((data_ref - data_inicio).days // 7) + 1


def semana_atual(hoje: date, data_inicio: date, num_semanas: int) -> int:
    """Semana corrente, limitada ao intervalo [1, num_semanas]."""
    s = semana_de(hoje, data_inicio)
    if s < 1:
        return 1
    if s > num_semanas:
        return num_semanas
    return s


def semana_no_intervalo(semana: int, num_semanas: int) -> bool:
    """Valida que a semana está dentro do programa (1..num_semanas)."""
    return 1 <= semana <= num_semanas


def niveis_anteriores(rows: list[tuple[int, UUID, int]], antes_de_semana: int) -> dict[UUID, int]:
    """Último nível conhecido por LO antes de uma semana.

    Args:
        rows: tuplas (semana, lo_id, nivel) do aluno (qualquer semana).
        antes_de_semana: considera apenas semanas estritamente menores que esta.

    Returns:
        Mapa lo_id -> nível da semana mais recente (< antes_de_semana) que possui aquele LO.
    """
    melhor_semana: dict[UUID, int] = {}
    resultado: dict[UUID, int] = {}
    for semana, lo_id, nivel in rows:
        if semana >= antes_de_semana:
            continue
        if lo_id not in melhor_semana or semana > melhor_semana[lo_id]:
            melhor_semana[lo_id] = semana
            resultado[lo_id] = nivel
    return resultado


def detectar_regressoes(
    niveis_atuais: dict[UUID, int], niveis_anteriores_por_lo: dict[UUID, int]
) -> list[tuple[UUID, int, int]]:
    """Detecta regressões: LO cujo nível atual é estritamente menor que o anterior comparável.

    Returns:
        Lista de (lo_id, nivel_atual, nivel_anterior) somente quando existe nível anterior
        comparável e o atual é menor.
    """
    regressoes: list[tuple[UUID, int, int]] = []
    for lo_id, atual in niveis_atuais.items():
        anterior = niveis_anteriores_por_lo.get(lo_id)
        if anterior is not None and atual < anterior:
            regressoes.append((lo_id, atual, anterior))
    return regressoes


# ──────────────────────────────────────────────
# Atestados Médicos — Cobertura de Turnos
# ──────────────────────────────────────────────


def periodo_valido(periodo_inicio: date, periodo_fim: date) -> bool:
    """Valida que o período do atestado é coerente (fim não anterior ao início)."""
    return periodo_fim >= periodo_inicio


def expandir_turnos_periodo(
    turma_ou_equipe: str, periodo_inicio: date, periodo_fim: date
) -> list[tuple[date, Turno, str]]:
    """Expande um período de atestado nos turnos esperados da turma.

    Para cada dia útil no intervalo ``[periodo_inicio, periodo_fim]`` (inclusivo), retorna
    os turnos esperados da turma naquele dia, cada um como uma tupla
    ``(data, turno, turno_referencia)`` onde ``turno_referencia`` é a chave
    ``"{YYYY-MM-DD}_{MANHA|TARDE}"`` usada pela exportação de frequência.

    Dias sem turno esperado (fim de semana, dias sem aula para a turma) não geram tuplas.
    Esta é uma função pura de domínio: NÃO filtra por presença de check-in — esse filtro
    acontece no caso de uso, que tem acesso ao banco.
    """
    if not periodo_valido(periodo_inicio, periodo_fim):
        return []

    resultado: list[tuple[date, Turno, str]] = []
    atual = periodo_inicio
    while atual <= periodo_fim:
        dia = _DIA_SEMANA_MAP.get(atual.weekday())
        if dia is not None:
            turnos = sorted(
                {c.turno for c in TURNOS_ALUNOS if c.turma == turma_ou_equipe and c.dia == dia},
                key=lambda t: t.value,
            )
            for turno in turnos:
                ref = f"{atual.isoformat()}_{turno.value}"
                resultado.append((atual, turno, ref))
        atual += timedelta(days=1)
    return resultado
