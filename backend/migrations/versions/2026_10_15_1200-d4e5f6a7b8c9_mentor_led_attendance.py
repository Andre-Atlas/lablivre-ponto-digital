"""mentor-led attendance: mentor_turmas, frequencias, users.status; descarta checkins

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-10-15 12:00:00

ATENÇÃO: esta migração é DESTRUTIVA — descarta os dados de auto-frequência
(`checkins` e `checkin_duplicatas`), conforme decisão do produto. Atestados e
avaliações são preservados. Faça backup antes de aplicar em produção.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None

status_aluno = sa.Enum("ATIVO", "DESLIGADO", name="statusaluno")
status_freq = sa.Enum("PRESENTE", "FALTA", "JUSTIFICADO", name="statusfrequencia")


def upgrade() -> None:
    bind = op.get_bind()

    # 1) Status do aluno
    status_aluno.create(bind, checkfirst=True)
    op.add_column(
        "users",
        sa.Column("status", status_aluno, nullable=False, server_default="ATIVO"),
    )

    # 2) Vínculo mentor–turma (N–N)
    op.create_table(
        "mentor_turmas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("turma", sa.String(length=100), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "turma", name="uq_mentor_turma"),
    )
    op.create_index("ix_mentor_turmas_turma", "mentor_turmas", ["turma"])

    # 3) Lançamento de frequência pelo mentor
    status_freq.create(bind, checkfirst=True)
    op.create_table(
        "frequencias",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("aluno_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("turma", sa.String(length=100), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("turno", sa.String(length=10), nullable=False),
        sa.Column("status", status_freq, nullable=False),
        sa.Column("mentor_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("atestado_documento", sa.LargeBinary(), nullable=True),
        sa.Column("atestado_filename", sa.String(length=255), nullable=True),
        sa.Column("atestado_content_type", sa.String(length=100), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("aluno_id", "data", "turno", name="uq_frequencia_aluno_data_turno"),
    )
    op.create_index("ix_frequencias_turma_data_turno", "frequencias", ["turma", "data", "turno"])

    # 4) DESCARTE dos dados de auto-frequência (modelo antigo)
    op.execute("DELETE FROM checkin_duplicatas")
    op.execute("DELETE FROM checkins")


def downgrade() -> None:
    op.drop_index("ix_frequencias_turma_data_turno", table_name="frequencias")
    op.drop_table("frequencias")
    op.drop_index("ix_mentor_turmas_turma", table_name="mentor_turmas")
    op.drop_table("mentor_turmas")
    op.drop_column("users", "status")
    bind = op.get_bind()
    status_freq.drop(bind, checkfirst=True)
    status_aluno.drop(bind, checkfirst=True)
    # Observação: os dados de checkins descartados no upgrade NÃO são restaurados.
