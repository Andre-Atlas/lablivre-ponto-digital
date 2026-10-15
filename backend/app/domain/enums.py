from __future__ import annotations

from enum import Enum


class TipoUsuario(str, Enum):
    ALUNO = "ALUNO"
    STAFF = "STAFF"


class StatusCheckin(str, Enum):
    PRESENTE = "PRESENTE"
    ATRASADO = "ATRASADO"
    FALTA = "FALTA"
    JUSTIFICADO = "JUSTIFICADO"


class RoleAdmin(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"
    NONE = "NONE"


class CertificateStatus(str, Enum):
    """Estado de um atestado médico."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class DiaSemana(str, Enum):
    SEG = "SEG"
    TER = "TER"
    QUA = "QUA"
    QUI = "QUI"
    SEX = "SEX"


class Turno(str, Enum):
    MANHA = "MANHA"
    TARDE = "TARDE"


class StatusAluno(str, Enum):
    """Situação do aluno no programa."""

    ATIVO = "ATIVO"
    DESLIGADO = "DESLIGADO"


class StatusFrequencia(str, Enum):
    """Estado de um lançamento de frequência feito pelo mentor."""

    PRESENTE = "PRESENTE"
    FALTA = "FALTA"
    JUSTIFICADO = "JUSTIFICADO"
