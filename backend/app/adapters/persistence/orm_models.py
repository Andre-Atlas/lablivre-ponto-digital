import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.domain.enums import (
    CertificateStatus,
    RoleAdmin,
    StatusAluno,
    StatusCheckin,
    StatusFrequencia,
    TipoUsuario,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoUsuario] = mapped_column(SAEnum(TipoUsuario), nullable=False)
    role: Mapped[RoleAdmin] = mapped_column(
        SAEnum(RoleAdmin), default=RoleAdmin.NONE, server_default="NONE", nullable=False
    )
    turma_ou_equipe: Mapped[str] = mapped_column(String(100), nullable=False)
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    oauth_sub: Mapped[str] = mapped_column(String(255), nullable=False)
    senha_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    patrimonio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    admin_aprovado: Mapped[bool] = mapped_column(Boolean, default=False)
    # Situação do aluno no programa (aplicável a tipo=ALUNO).
    status: Mapped[StatusAluno] = mapped_column(
        SAEnum(StatusAluno), default=StatusAluno.ATIVO, server_default="ATIVO", nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    devices: Mapped[list["Device"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    checkins: Mapped[list["Checkin"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__ = (
        Index("ix_users_tipo", "tipo"),
        Index("ix_users_turma_ou_equipe", "turma_ou_equipe"),
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    mac_address: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    os_type: Mapped[str] = mapped_column(String(50), nullable=False)
    principal: Mapped[bool] = mapped_column(Boolean, default=True)
    registrado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="devices")
    checkins: Mapped[list["Checkin"]] = relationship(
        back_populates="device", cascade="all, delete-orphan", passive_deletes=True
    )


class Checkin(Base):
    __tablename__ = "checkins"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), nullable=False
    )
    hora_checkin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_publico: Mapped[str | None] = mapped_column(String(45), nullable=True)
    ssid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bssids: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    status: Mapped[StatusCheckin] = mapped_column(SAEnum(StatusCheckin), nullable=False)
    turno_referencia: Mapped[str] = mapped_column(String(50), nullable=False)
    exportado_sheets: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="checkins")
    device: Mapped["Device"] = relationship(back_populates="checkins")
    duplicatas: Mapped[list["CheckinDuplicata"]] = relationship(
        back_populates="checkin_original", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint("user_id", "turno_referencia", name="uq_checkin_user_turno"),
        Index("ix_checkins_user_turno", "user_id", "turno_referencia"),
        Index("ix_checkins_criado_em", "criado_em"),
    )


class CheckinDuplicata(Base):
    __tablename__ = "checkin_duplicatas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    checkin_original_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("checkins.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), nullable=False
    )
    hora_tentativa: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_publico: Mapped[str | None] = mapped_column(String(45), nullable=True)
    motivo: Mapped[str] = mapped_column(String(100), default="DUPLICATA_MESMO_TURNO")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    checkin_original: Mapped["Checkin"] = relationship(back_populates="duplicatas")


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleAdmin] = mapped_column(SAEnum(RoleAdmin), nullable=False)
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    oauth_sub: Mapped[str] = mapped_column(String(255), nullable=False)
    senha_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MedicalCertificate(Base):
    __tablename__ = "medical_certificates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    periodo_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    periodo_fim: Mapped[date] = mapped_column(Date, nullable=False)
    documento: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    documento_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    documento_content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    documento_tamanho: Mapped[int] = mapped_column(Integer, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CertificateStatus] = mapped_column(
        SAEnum(CertificateStatus),
        default=CertificateStatus.ACTIVE,
        server_default="ACTIVE",
        nullable=False,
    )
    registrado_por: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    revogado_por: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    motivo_revogacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revogado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    dias: Mapped[list["CertificateDay"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__ = (
        Index("ix_medical_certificates_user", "user_id"),
        Index("ix_medical_certificates_user_periodo", "user_id", "periodo_inicio", "periodo_fim"),
        Index("ix_medical_certificates_status", "status"),
    )


class CertificateDay(Base):
    __tablename__ = "certificate_days"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    certificate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medical_certificates.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    turno: Mapped[str] = mapped_column(String(50), nullable=False)
    turno_referencia: Mapped[str] = mapped_column(String(50), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    certificate: Mapped["MedicalCertificate"] = relationship(back_populates="dias")

    __table_args__ = (
        UniqueConstraint("certificate_id", "turno_referencia", name="uq_certificate_day"),
        Index("ix_certificate_days_lookup", "user_id", "turno_referencia", "ativo"),
        Index("ix_certificate_days_certificate", "certificate_id"),
    )


class Config(Base):
    __tablename__ = "config"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    chave: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    atualizado_por: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("admins.id", ondelete="SET NULL"), nullable=True
    )


class IpAllowlist(Base):
    __tablename__ = "ip_allowlist"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ip_cidr: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BssidAllowlist(Base):
    __tablename__ = "bssid_allowlist"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bssid: Mapped[str] = mapped_column(String(17), nullable=False)
    ssid_associado: Mapped[str | None] = mapped_column(String(255), nullable=True)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LearningOutcome(Base):
    __tablename__ = "learning_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("numero", name="uq_lo_numero"),
        Index("ix_learning_outcomes_ativo", "ativo"),
    )


class WeeklyEvaluation(Base):
    __tablename__ = "lo_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    semana: Mapped[int] = mapped_column(Integer, nullable=False)
    turma: Mapped[str] = mapped_column(String(100), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    niveis: Mapped[list["EvaluationLevel"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan", passive_deletes=True
    )
    comentarios: Mapped[list["EvaluationComment"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint("user_id", "semana", name="uq_evaluation_user_semana"),
        Index("ix_evaluations_turma_semana", "turma", "semana"),
    )


class EvaluationLevel(Base):
    __tablename__ = "lo_evaluation_levels"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lo_evaluations.id", ondelete="CASCADE"), nullable=False
    )
    lo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("learning_outcomes.id", ondelete="RESTRICT"), nullable=False
    )
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    evaluation: Mapped["WeeklyEvaluation"] = relationship(back_populates="niveis")

    __table_args__ = (
        UniqueConstraint("evaluation_id", "lo_id", name="uq_level_evaluation_lo"),
        Index("ix_evaluation_levels_lo", "lo_id"),
    )


class EvaluationComment(Base):
    __tablename__ = "lo_evaluation_comments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lo_evaluations.id", ondelete="CASCADE"), nullable=False
    )
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    mentor_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    evaluation: Mapped["WeeklyEvaluation"] = relationship(back_populates="comentarios")

    __table_args__ = (
        UniqueConstraint("evaluation_id", "mentor_id", name="uq_comment_evaluation_mentor"),
    )


class MentorTurma(Base):
    """Vínculo N–N entre mentor (usuário STAFF/ADMIN) e turma (nome)."""

    __tablename__ = "mentor_turmas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    turma: Mapped[str] = mapped_column(String(100), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "turma", name="uq_mentor_turma"),
        Index("ix_mentor_turmas_turma", "turma"),
    )


class Frequencia(Base):
    """Lançamento de frequência feito por um mentor (fonte de verdade da presença)."""

    __tablename__ = "frequencias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    aluno_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    turma: Mapped[str] = mapped_column(String(100), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    turno: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[StatusFrequencia] = mapped_column(SAEnum(StatusFrequencia), nullable=False)
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Atestado anexado por turno (quando Falta justificada); cobre apenas este lançamento.
    atestado_documento: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    atestado_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    atestado_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("aluno_id", "data", "turno", name="uq_frequencia_aluno_data_turno"),
        Index("ix_frequencias_turma_data_turno", "turma", "data", "turno"),
    )
