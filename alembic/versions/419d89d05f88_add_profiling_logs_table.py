"""add profiling_logs table

Revision ID: 419d89d05f88
Revises: 26205302d89c
Create Date: 2025-11-25 13:17:18.404662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '419d89d05f88'
down_revision: Union[str, Sequence[str], None] = '26205302d89c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "profiling_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        
        # Infos sur la requête
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        
        # Métriques globales
        sa.Column("total_time_ms", sa.Float(), nullable=False),
        sa.Column("num_predictions", sa.Integer(), nullable=False, server_default=sa.text("0")),
        
        # Breakdown détaillé (temps en ms)
        sa.Column("time_preprocessing_ms", sa.Float(), nullable=True),
        sa.Column("time_inference_ms", sa.Float(), nullable=True),
        sa.Column("time_database_ms", sa.Float(), nullable=True),
        sa.Column("time_serialization_ms", sa.Float(), nullable=True),
        
        # Top fonctions lentes (JSON)
        sa.Column("top_functions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        
        # Nombre d'appels par catégorie
        sa.Column("ncalls_total", sa.Integer(), nullable=True),
        sa.Column("ncalls_pandas", sa.Integer(), nullable=True),
        sa.Column("ncalls_database", sa.Integer(), nullable=True),
        
        # Stats système
        sa.Column("cpu_percent", sa.Float(), nullable=True),
        sa.Column("memory_mb", sa.Float(), nullable=True),
        
        # Profil complet (optionnel, pour debug)
        sa.Column("full_profile", sa.Text(), nullable=True),
    )

    # Index simples
    op.create_index("ix_profiling_logs_endpoint", "profiling_logs", ["endpoint"], unique=False)
    op.create_index("ix_profiling_logs_created_at", "profiling_logs", ["created_at"], unique=False)
    op.create_index("ix_profiling_logs_model_name", "profiling_logs", ["model_name"], unique=False)
    
    # Index composites utiles pour les dashboards Grafana
    op.create_index(
        "ix_profiling_logs_endpoint_created",
        "profiling_logs",
        ["endpoint", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_profiling_logs_model_created",
        "profiling_logs",
        ["model_name", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop des index composites
    op.drop_index("ix_profiling_logs_model_created", table_name="profiling_logs")
    op.drop_index("ix_profiling_logs_endpoint_created", table_name="profiling_logs")
    
    # Drop des index simples
    op.drop_index("ix_profiling_logs_model_name", table_name="profiling_logs")
    op.drop_index("ix_profiling_logs_created_at", table_name="profiling_logs")
    op.drop_index("ix_profiling_logs_endpoint", table_name="profiling_logs")
    
    # Drop de la table
    op.drop_table("profiling_logs")