# src/models/ml_output.py
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base


class MLOutput(Base):
    __tablename__ = "ml_outputs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    input_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ml_inputs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


    request_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    model_name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    prediction: Mapped[str] = mapped_column(String(255), nullable=False)
    prob: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    proba_defaut: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    proba_solvable: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    classes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    error: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        Index("ix_ml_outputs_model_created", "model_name", "created_at"),
        Index("ix_ml_outputs_request_created", "request_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<MLOutput id={self.id} input_id={self.input_id} "
            f"model={self.model_name}@{self.model_version} "
            f"prediction={self.prediction} prob={self.prob}>"
        )
