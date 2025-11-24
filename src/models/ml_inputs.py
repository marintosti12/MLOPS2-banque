import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from .base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB

class MLInput(Base):
    __tablename__ = "ml_inputs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    model_name: Mapped[str] = mapped_column(String(100), index=True)

    raw_data: Mapped[dict] = mapped_column(JSONB)

    features: Mapped[dict] = mapped_column(JSONB, nullable=True)
