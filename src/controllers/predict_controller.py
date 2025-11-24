from datetime import datetime, timezone
from uuid import uuid4
import math

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
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
    summary="Prédire la solvabilité d’un client (credit scoring)",
    description=(
        "Calcule la probabilité qu’un dossier soit **solvable**.\n\n"
        "**Notes**\n"
        "- `model_name` doit référencer un modèle *actif* en base (`MLModel`).\n"
        "- Les données d’entrée sont persistées (`MLInput`) puis les sorties (`MLOutput`) sont enregistrées.\n"
        "- En cas d’erreur de préparation des features ou de prédiction, la requête retourne **400**.\n"
        "- Les colonnes attendues correspondent à votre préprocesseur (`num_cols` / `cat_cols`).\n"
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

    row = db.query(MLModel).filter(MLModel.name == payload.model_name).first()
    if not row or getattr(row, "is_active", True) is False:
        raise HTTPException(status_code=404, detail="Modèle introuvable ou inactif")

    try:
        model = load_model(payload.model_name)
        classes = getattr(model, "classes_", [0, 1])
        classes = [int(c) for c in classes]
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Chargement du modèle '{payload.model_name}' impossible: {e}",
        )

    # --- Préparation des features ---
    try:
        df_raw = pd.DataFrame([x.model_dump() for x in payload.inputs])

        try:
            X = compute_features(df_raw.copy())
        except Exception:
            # fallback sans préprocessing si problème
            X = df_raw.copy()

        X = X.reset_index(drop=True)
        df_raw = df_raw.reset_index(drop=True)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de préparation des features: {e}",
        )

    request_id = str(uuid4())
    now = datetime.now(timezone.utc)

    # --- Persistance des entrées (MLInput) ---
    try:
        ml_input_rows: list[MLInput] = []
        for i in range(len(df_raw)):
            raw_dict = series_to_jsonable(df_raw.iloc[i])
            feat_dict = series_to_jsonable(X.iloc[i])

            ml_input = MLInput(
                created_at=now,
                model_name=payload.model_name,
                raw_data=raw_dict,
                features=feat_dict,
            )
            ml_input_rows.append(ml_input)

        db.add_all(ml_input_rows)
        db.flush()

    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors de l'enregistrement des entrées: {e}",
        )

    # --- Prédiction & persistance des sorties (MLOutput) ---
    try:
        probas = model.predict_proba(X)
        i_def = classes.index(1)
        i_sol = classes.index(0)
        THRESH = 0.5

        results: list[PredictItemResult] = []
        ml_output_rows: list[MLOutput] = []

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

            ml_out = MLOutput(
                input_id=ml_input_rows[i].id,
                model_name=payload.model_name,
                model_version=getattr(row, "version", None),
                prediction=label,
                prob=proba_retour,
                proba_defaut=p_def,
                proba_solvable=p_sol,
                threshold=THRESH,
                classes=classes,
                latency_ms=elapsed_ms,     
                meta={
                    "request_id": request_id,
                    "elapsed_ms": elapsed_ms,
                },
                created_at=now,
            )
            ml_output_rows.append(ml_out)

        db.add_all(ml_output_rows)
        db.commit()

    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Erreur pendant la prédiction: {e}",
        )

    return PredictResponse(
        model_name=payload.model_name,
        results=results,
    )
