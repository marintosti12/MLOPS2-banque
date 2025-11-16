"""create ml_outputs

Revision ID: 26205302d89c
Revises: 139f2b88b435
Create Date: 2025-11-10 14:20:26.932125

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '26205302d89c'
down_revision: Union[str, Sequence[str], None] = '139f2b88b435'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ml_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "input_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ml_inputs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("request_id", sa.String(length=64), nullable=True),

        sa.Column("model_name", sa.String(length=255), nullable=True),
        sa.Column("model_version", sa.String(length=64), nullable=True),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("latency_ms", sa.Integer(), nullable=True),

        sa.Column("prediction", sa.String(length=255), nullable=False),
        sa.Column("prob", sa.Float(), nullable=True),
        sa.Column("proba_defaut", sa.Float(), nullable=True),
        sa.Column("proba_solvable", sa.Float(), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),

        sa.Column("classes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        sa.Column("error", sa.String(length=500), nullable=True),
    )

    # Index simples (conformes aux flags index=True du modèle)
    op.create_index("ix_ml_outputs_input_id", "ml_outputs", ["input_id"], unique=False)
    op.create_index("ix_ml_outputs_request_id", "ml_outputs", ["request_id"], unique=False)
    op.create_index("ix_ml_outputs_model_name", "ml_outputs", ["model_name"], unique=False)
    op.create_index("ix_ml_outputs_created_at", "ml_outputs", ["created_at"], unique=False)

    # Index composites utiles pour les requêtes/dashboards
    op.create_index(
        "ix_ml_outputs_model_created",
        "ml_outputs",
        ["model_name", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_ml_outputs_request_created",
        "ml_outputs",
        ["request_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop des index composites
    op.drop_index("ix_ml_outputs_request_created", table_name="ml_outputs")
    op.drop_index("ix_ml_outputs_model_created", table_name="ml_outputs")

    # Drop des index simples
    op.drop_index("ix_ml_outputs_created_at", table_name="ml_outputs")
    op.drop_index("ix_ml_outputs_model_name", table_name="ml_outputs")
    op.drop_index("ix_ml_outputs_request_id", table_name="ml_outputs")
    op.drop_index("ix_ml_outputs_input_id", table_name="ml_outputs")

    # Drop de la table
    op.drop_table("ml_outputs")