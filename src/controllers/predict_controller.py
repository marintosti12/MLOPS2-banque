from datetime import datetime, timezone
from uuid import uuid4
import math

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from sqlalchemy import insert
import pandas as pd
import numpy as np  

from src.config.db import get_db
from src.models.ml import MLModel
from src.models.ml_inputs import MLInput
from src.models.ml_output import MLOutput

from src.model_loader import load_model
from src.features import compute_features

from src.schemas.PredictItemResult import PredictItemResult
from src.schemas.PredictResponse import PredictResponse
from src.schemas.PredictRequest import PredictRequest 

from time import perf_counter

router = APIRouter(prefix="/predict", tags=["Solvabilité"])

LABELS = {
    "0": "non_solvable",
    "1": "solvable",
}


def series_to_jsonable(s: pd.Series) -> dict:
    cleaned: dict = {}
    for k, v in s.items():
        if v is pd.NaT:
            cleaned[k] = None
            continue

        if isinstance(v, np.floating):
            if np.isnan(v):
                cleaned[k] = None
            else:
                cleaned[k] = float(v)
            continue

        if isinstance(v, np.integer):
            cleaned[k] = int(v)
            continue

        if isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                cleaned[k] = None
            else:
                cleaned[k] = v
            continue

        cleaned[k] = v

    return cleaned


@router.post(
    "/",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Prédire la solvabilité d'un client (credit scoring)",
    description=(
        "Calcule la probabilité qu'un dossier soit **solvable**.\n\n"
        "**Notes**\n"
        "- `model_name` doit référencer un modèle *actif* en base (`MLModel`).\n"
        "- Les données d'entrée sont persistées (`MLInput`) puis les sorties (`MLOutput`) sont enregistrées.\n"
        "- En cas d'erreur de préparation des features ou de prédiction, la requête retourne **400**.\n"
    ),
    responses={
        200: {"description": "Prédictions calculées avec succès."},
        400: {"description": "Erreur pendant la préparation des features ou la prédiction."},
        404: {"description": "Modèle introuvable ou inactif."},
        500: {"description": "Impossible de charger le modèle/erreur serveur."},
    },
)
def batch_predict(
    payload: PredictRequest = Body(...),
    db: Session = Depends(get_db),
):
    start_time = perf_counter()
    request_id = str(uuid4())
    now = datetime.now(timezone.utc)

    row = db.query(MLModel).filter(MLModel.name == payload.model_name).first()
    if not row or getattr(row, "is_active", True) is False:
        raise HTTPException(status_code=404, detail="Modèle introuvable ou inactif")

    try:
        model = load_model(payload.model_name)
        classes = getattr(model, "classes_", [0, 1])
        classes = [int(c) for c in classes]
    except Exception as e:
        print(f"[ERROR] Chargement modèle: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chargement du modèle '{payload.model_name}' impossible: {e}",
        )

    try:
        df_raw = pd.DataFrame([x.model_dump() for x in payload.inputs])

        try:
            X = compute_features(df_raw.copy())
        except Exception:
            X = df_raw.copy()

        X = X.reset_index(drop=True)
        df_raw = df_raw.reset_index(drop=True)

    except Exception as e:
        print(f"[ERROR] Préparation features: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de préparation des features: {e}",
        )

    try:
        input_dicts = []
        for i in range(len(df_raw)):
            raw_dict = series_to_jsonable(df_raw.iloc[i])
            feat_dict = series_to_jsonable(X.iloc[i])

            input_dicts.append({
                "created_at": now,
                "model_name": payload.model_name,
                "raw_data": raw_dict,
                "features": feat_dict,
            })

        stmt = insert(MLInput).returning(MLInput.id)
        result = db.execute(stmt, input_dicts)
        input_ids = [row[0] for row in result.fetchall()]

    except Exception as e:
        print(f"[ERROR] Bulk insert MLInput: {e}")
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors de l'enregistrement des entrées: {e}",
        )

    try:
        probas = model.predict_proba(X)
        i_def = classes.index(1)
        i_sol = classes.index(0)
        THRESH = 0.5

        results: list[PredictItemResult] = []
        output_dicts = []

        elapsed_ms = int((perf_counter() - start_time) * 1000)

        for i, p in enumerate(probas):
            p_def = float(p[i_def])
            p_sol = float(p[i_sol])

            if p_def >= THRESH:
                label = "non_solvable"
                proba_retour = p_def
            else:
                label = "solvable"
                proba_retour = p_sol

            results.append(
                PredictItemResult(label=label, proba=proba_retour)
            )

            output_dicts.append({
                "input_id": input_ids[i],
                "model_name": payload.model_name,
                "model_version": getattr(row, "version", None),
                "prediction": label,
                "prob": proba_retour,
                "proba_defaut": p_def,
                "proba_solvable": p_sol,
                "threshold": THRESH,
                "classes": classes,
                "latency_ms": elapsed_ms,
                "meta": {
                    "request_id": request_id,
                    "elapsed_ms": elapsed_ms,
                },
                "created_at": now,
            })

        db.execute(insert(MLOutput), output_dicts)

        db.commit()

    except Exception as e:
        print(f"[ERROR] Prédiction/bulk insert: {e}")
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Erreur pendant la prédiction: {e}",
        )

    return PredictResponse(
        model_name=payload.model_name,
        results=results,
    )