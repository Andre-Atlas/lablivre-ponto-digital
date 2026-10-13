"""add medical certificates and certificate days

Revision ID: b1c2d3e4f5a6
Revises: a02dab1dca18
Create Date: 2026-10-09 17:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5a6"
down_revision: str | Sequence[str] | None = "a02dab1dca18"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "medical_certificates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("periodo_inicio", sa.Date(), nullable=False),
        sa.Column("periodo_fim", sa.Date(), nullable=False),
        sa.Column("documento", sa.LargeBinary(), nullable=False),
        sa.Column("documento_filename", sa.String(length=255), nullable=False),
        sa.Column("documento_content_type", sa.String(length=100), nullable=False),
        sa.Column("documento_tamanho", sa.Integer(), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "REVOKED", name="certificatestatus"),
            server_default="ACTIVE",
            nullable=False,
        ),
        sa.Column("registrado_por", sa.Uuid(), nullable=True),
        sa.Column("revogado_por", sa.Uuid(), nullable=True),
        sa.Column("motivo_revogacao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("revogado_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["registrado_por"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["revogado_por"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_medical_certificates_user", "medical_certificates", ["user_id"], unique=False
    )
    op.create_index(
        "ix_medical_certificates_user_periodo",
        "medical_certificates",
        ["user_id", "periodo_inicio", "periodo_fim"],
        unique=False,
    )
    op.create_index(
        "ix_medical_certificates_status", "medical_certificates", ["status"], unique=False
    )

    op.create_table(
        "certificate_days",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("certificate_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("turno", sa.String(length=50), nullable=False),
        sa.Column("turno_referencia", sa.String(length=50), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["certificate_id"], ["medical_certificates.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("certificate_id", "turno_referencia", name="uq_certificate_day"),
    )
    op.create_index(
        "ix_certificate_days_lookup",
        "certificate_days",
        ["user_id", "turno_referencia", "ativo"],
        unique=False,
    )
    op.create_index(
        "ix_certificate_days_certificate", "certificate_days", ["certificate_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_certificate_days_certificate", table_name="certificate_days")
    op.drop_index("ix_certificate_days_lookup", table_name="certificate_days")
    op.drop_table("certificate_days")
    op.drop_index("ix_medical_certificates_status", table_name="medical_certificates")
    op.drop_index("ix_medical_certificates_user_periodo", table_name="medical_certificates")
    op.drop_index("ix_medical_certificates_user", table_name="medical_certificates")
    op.drop_table("medical_certificates")
    sa.Enum(name="certificatestatus").drop(op.get_bind(), checkfirst=True)
