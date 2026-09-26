from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, ForeignKey, Text, UniqueConstraint, Index, Uuid, JSON
from sqlalchemy.sql import func
import uuid
from datetime import datetime
import enum
from typing import List, Optional, Any

class Base(DeclarativeBase):
    pass

class TipoUsuario(str, enum.Enum):
    ALUNO = 'ALUNO'
    STAFF = 'STAFF'

class StatusCheckin(str, enum.Enum):
    PRESENTE = 'PRESENTE'
    ATRASADO = 'ATRASADO'

class RoleAdmin(str, enum.Enum):
    SUPER_ADMIN = 'SUPER_ADMIN'
    ADMIN = 'ADMIN'
    VIEWER = 'VIEWER'

class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoUsuario] = mapped_column(SAEnum(TipoUsuario), nullable=False)
    turma_ou_equipe: Mapped[str] = mapped_column(String(100), nullable=False)
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    oauth_sub: Mapped[str] = mapped_column(String(255), nullable=False)
    senha_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    patrimonio: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    admin_aprovado: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    devices: Mapped[List["Device"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    checkins: Mapped[List["Checkin"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        Index('ix_users_tipo', 'tipo'),
        Index('ix_users_turma_ou_equipe', 'turma_ou_equipe'),
    )

class Device(Base):
    __tablename__ = 'devices'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    mac_address: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    os_type: Mapped[str] = mapped_column(String(50), nullable=False)
    principal: Mapped[bool] = mapped_column(Boolean, default=True)
    registrado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="devices")
    checkins: Mapped[List["Checkin"]] = relationship(back_populates="device", cascade="all, delete-orphan", passive_deletes=True)

class Checkin(Base):
    __tablename__ = 'checkins'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    hora_checkin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_publico: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    ssid: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bssids: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    status: Mapped[StatusCheckin] = mapped_column(SAEnum(StatusCheckin), nullable=False)
    turno_referencia: Mapped[str] = mapped_column(String(50), nullable=False)
    exportado_sheets: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="checkins")
    device: Mapped["Device"] = relationship(back_populates="checkins")
    duplicatas: Mapped[List["CheckinDuplicata"]] = relationship(back_populates="checkin_original", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'turno_referencia', name='uq_checkin_user_turno'),
        Index('ix_checkins_user_turno', 'user_id', 'turno_referencia'),
        Index('ix_checkins_criado_em', 'criado_em'),
    )

class CheckinDuplicata(Base):
    __tablename__ = 'checkin_duplicatas'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    checkin_original_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('checkins.id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    hora_tentativa: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_publico: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    motivo: Mapped[str] = mapped_column(String(100), default='DUPLICATA_MESMO_TURNO')
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    checkin_original: Mapped["Checkin"] = relationship(back_populates="duplicatas")

class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleAdmin] = mapped_column(SAEnum(RoleAdmin), nullable=False)
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    oauth_sub: Mapped[str] = mapped_column(String(255), nullable=False)
    senha_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
class Config(Base):
    __tablename__ = 'config'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    chave: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    atualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('admins.id', ondelete='SET NULL'), nullable=True)

class IpAllowlist(Base):
    __tablename__ = 'ip_allowlist'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ip_cidr: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class BssidAllowlist(Base):
    __tablename__ = 'bssid_allowlist'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bssid: Mapped[str] = mapped_column(String(17), nullable=False)
    ssid_associado: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    descricao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
