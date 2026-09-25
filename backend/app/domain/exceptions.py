"""Exceções de domínio do Ponto Digital.

Exceções específicas do negócio, sem referência a códigos HTTP
(a tradução para HTTP status ocorre na camada de API).
"""

from uuid import UUID
from datetime import datetime


class DomainError(Exception):
    """Exceção base do domínio."""

    pass


class ForaTurnoError(DomainError):
    """Lançada quando não há turno ativo para a turma do usuário no momento."""

    pass


class RedeNaoAutorizadaError(DomainError):
    """Lançada quando o IP ou rede não está na lista permitida."""

    pass


class ForaDoRaioError(DomainError):
    """Lançada quando a localização está fora do raio de geofencing permitido."""

    def __init__(self, distancia_metros: float) -> None:
        self.distancia_metros = distancia_metros
        super().__init__(
            f"Fora do raio de check-in. Distância: {distancia_metros:.2f}m."
        )


class UsuarioNaoAprovadoError(DomainError):
    """Lançada quando o usuário ainda não foi aprovado pelo administrador."""

    pass


class UsuarioInativoError(DomainError):
    """Lançada quando o usuário está desativado no sistema."""

    pass


class DuplicataError(DomainError):
    """Lançada quando já existe um check-in válido para este turno."""

    def __init__(self, checkin_original_id: UUID, hora_original: datetime) -> None:
        self.checkin_original_id = checkin_original_id
        self.hora_original = hora_original
        super().__init__(
            f"Check-in duplicado. Original: {checkin_original_id} "
            f"em {hora_original.isoformat()}."
        )


class DispositivoNaoRegistradoError(DomainError):
    """Lançada quando o dispositivo não está registrado para o usuário."""

    pass


class PatrimonioObrigatorioError(DomainError):
    """Lançada quando falta o número de patrimônio para usuários do tipo ALUNO."""

    pass


class EmailDuplicadoError(DomainError):
    """Lançada quando o e-mail já está registrado no sistema."""

    pass
