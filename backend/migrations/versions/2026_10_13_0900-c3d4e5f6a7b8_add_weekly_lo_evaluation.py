"""add weekly LO evaluation tables

Revision ID: c3d4e5f6a7b8
Revises: a02dab1dca18
Create Date: 2026-10-13 09:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: str | Sequence[str] | None = "a02dab1dca18"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "learning_outcomes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("numero", name="uq_lo_numero"),
    )
    op.create_index("ix_learning_outcomes_ativo", "learning_outcomes", ["ativo"], unique=False)

    op.create_table(
        "lo_evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("semana", sa.Integer(), nullable=False),
        sa.Column("turma", sa.String(length=100), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "semana", name="uq_evaluation_user_semana"),
    )
    op.create_index(
        "ix_evaluations_turma_semana", "lo_evaluations", ["turma", "semana"], unique=False
    )

    op.create_table(
        "lo_evaluation_levels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("evaluation_id", sa.Uuid(), nullable=False),
        sa.Column("lo_id", sa.Uuid(), nullable=False),
        sa.Column("nivel", sa.Integer(), nullable=False),
        sa.Column("mentor_id", sa.Uuid(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["evaluation_id"], ["lo_evaluations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lo_id"], ["learning_outcomes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluation_id", "lo_id", name="uq_level_evaluation_lo"),
    )
    op.create_index("ix_evaluation_levels_lo", "lo_evaluation_levels", ["lo_id"], unique=False)

    op.create_table(
        "lo_evaluation_comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("evaluation_id", sa.Uuid(), nullable=False),
        sa.Column("mentor_id", sa.Uuid(), nullable=True),
        sa.Column("mentor_nome", sa.String(length=255), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["evaluation_id"], ["lo_evaluations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluation_id", "mentor_id", name="uq_comment_evaluation_mentor"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("lo_evaluation_comments")
    op.drop_index("ix_evaluation_levels_lo", table_name="lo_evaluation_levels")
    op.drop_table("lo_evaluation_levels")
    op.drop_index("ix_evaluations_turma_semana", table_name="lo_evaluations")
    op.drop_table("lo_evaluations")
    op.drop_index("ix_learning_outcomes_ativo", table_name="learning_outcomes")
    op.drop_table("learning_outcomes")
