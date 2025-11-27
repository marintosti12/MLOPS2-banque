from datetime import datetime, timezone
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.config.db import get_db
from src.models.ml import MLModel


def test_list_ml_models_simple(tmp_path):
    db_path = tmp_path / "testing.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    SQLSession = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    MLModel.__table__.create(bind=engine)

    session = SQLSession()

    def get_db_override():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app, raise_server_exceptions=False)

    created = datetime(2025, 9, 15, 10, 11, 3, 950802, tzinfo=timezone.utc)
    session.add_all(
        [
            MLModel(
                id=uuid.UUID("5b1c7b3a-0000-4000-8000-000000000001"),
                name="baseline",
                description="Baseline model",
                created_at=created,
                is_active=True,
            ),
            MLModel(
                id=uuid.UUID("5b1c7b3a-0000-4000-8000-000000000002"),
                name="best_model",
                description="XGB v1",
                created_at=created,
                is_active=True,
            ),
            MLModel(
                id=uuid.UUID("5b1c7b3a-0000-4000-8000-000000000003"),
                name="logistic_regression",
                description="Logistic Regression",
                created_at=created,
                is_active=True,
            ),
        ]
    )
    session.commit()

    resp = client.get("/")

    app.dependency_overrides.clear()
    session.close()

    assert resp.status_code == 200
    data = resp.json()
    names = {row["name"] for row in data}
    assert names == {"baseline", "best_model", "logistic_regression"}
