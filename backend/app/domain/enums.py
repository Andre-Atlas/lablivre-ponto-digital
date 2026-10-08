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

class DiaSemana(str, Enum):
    SEG = "SEG"
    TER = "TER"
    QUA = "QUA"
    QUI = "QUI"
    SEX = "SEX"

class Turno(str, Enum):
    MANHA = "MANHA"
    TARDE = "TARDE"
