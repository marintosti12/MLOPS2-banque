"""create ml_inputs

Revision ID: 139f2b88b435
Revises: 99e339b56253
Create Date: 2025-11-10 14:13:40.494066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision: str = '139f2b88b435'
down_revision: Union[str, Sequence[str], None] = '99e339b56253'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "ml_inputs",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),  
        ),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=True),
        sa.Column("raw_data", pg.JSONB, nullable=False),
        sa.Column("features", pg.JSONB, nullable=True),
    )

    op.create_index(
        "ix_ml_inputs_created_at",
        "ml_inputs",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_ml_inputs_model_name",
        "ml_inputs",
        ["model_name"],
        unique=False,
    )

    op.create_index(
        "ix_ml_inputs_raw_data_gin",
        "ml_inputs",
        ["raw_data"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_ml_inputs_features_gin",
        "ml_inputs",
        ["features"],
        postgresql_using="gin",
    )


def downgrade():
    op.drop_index("ix_ml_inputs_features_gin", table_name="ml_inputs")
    op.drop_index("ix_ml_inputs_raw_data_gin", table_name="ml_inputs")
    op.drop_index("ix_ml_inputs_model_name", table_name="ml_inputs")
    op.drop_index("ix_ml_inputs_created_at", table_name="ml_inputs")
    op.drop_table("ml_inputs")
