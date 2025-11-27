from datetime import datetime, timezone
import uuid

import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles

from src.main import app
from src.config.db import get_db
from src.models.ml import MLModel
from src.models.ml_inputs import MLInput
from src.models.ml_output import MLOutput


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


def test_batch_predict_simple(tmp_path, monkeypatch):
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
    MLInput.__table__.create(bind=engine)
    MLOutput.__table__.create(bind=engine)

    session = SQLSession()

    def get_db_override():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app, raise_server_exceptions=False)

    created = datetime(2025, 9, 15, 10, 11, 3, 950802, tzinfo=timezone.utc)
    model_row = MLModel(
        id=uuid.uuid4(),
        name="best_model",
        description="XGB v1",
        created_at=created,
        is_active=True,
    )
    session.add(model_row)
    session.commit()

    class FakeModel:
        classes_ = [0, 1]  

        def predict_proba(self, X: pd.DataFrame):
            return [[0.3, 0.7] for _ in range(len(X))]

    import src.controllers.predict_controller as pc

    def fake_load_model(name: str):
        assert name == "best_model"
        return FakeModel()

    def fake_compute_features(df: pd.DataFrame) -> pd.DataFrame:
        return df

    monkeypatch.setattr(pc, "load_model", fake_load_model)
    monkeypatch.setattr(pc, "compute_features", fake_compute_features)


    payload = {
        "model_name": "best_model",
        "inputs": [
            {
                "SK_ID_CURR": 100005,
                "NAME_CONTRACT_TYPE": "Cash loans",
                "CODE_GENDER": "M",
                "FLAG_OWN_CAR": "N",
                "FLAG_OWN_REALTY": "Y",
                "CNT_CHILDREN": 0,
                "AMT_INCOME_TOTAL": 99000.0,
                "AMT_CREDIT": 222768.0,
                "AMT_ANNUITY": 17370.0,
                "AMT_GOODS_PRICE": 180000.0,
                "NAME_TYPE_SUITE": "Unaccompanied",
                "NAME_INCOME_TYPE": "Working",
                "NAME_EDUCATION_TYPE": "Secondary / secondary special",
                "NAME_FAMILY_STATUS": "Married",
                "NAME_HOUSING_TYPE": "House / apartment",
                "REGION_POPULATION_RELATIVE": 0.035792000000000004,
                "DAYS_BIRTH": -18064,
                "DAYS_EMPLOYED": -4469,
                "DAYS_REGISTRATION": -9118,
                "DAYS_ID_PUBLISH": -1623,
                "OCCUPATION_TYPE": "Low-skill Laborers",
                "WEEKDAY_APPR_PROCESS_START": "FRIDAY",
                "HOUR_APPR_PROCESS_START": 9,
                "ORGANIZATION_TYPE": "Self-employed",
                "EXT_SOURCE_1": 0.5649902017969249,
                "EXT_SOURCE_2": 0.2916555320093651,
                "EXT_SOURCE_3": 0.4329616670974407,
                "AMT_REQ_CREDIT_BUREAU_YEAR": 3.0,
            }
        ],
    }

    resp = client.post("/predict/", json=payload)

    app.dependency_overrides.clear()
    session.close()

    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["model_name"] == "best_model"
    assert "results" in body
    assert len(body["results"]) == 1

    item = body["results"][0]
    assert item["label"] in ("solvable", "non_solvable")
    assert 0.0 <= item["proba"] <= 1.0
