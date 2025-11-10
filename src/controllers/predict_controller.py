from fastapi import APIRouter, Depends, HTTPException, Body, status

from config.db import get_db
from models.ml import MLModel 

from models.ml_inputs import MLInput
from models.ml_output import MLOutput

import pandas as pd
from model_loader import load_model           
from features import compute_features
from schemas.PredictItemResult import PredictItemResult
from schemas.PredictResponse import PredictResponse
from schemas.PredictRequest import PredictRequest
from sqlalchemy.orm import Session

router = APIRouter(prefix="/predict", tags=["Prédiction"])

LABELS = {
    "0": "reste_dans_l_entreprise",
    "1": "parti_de_l_entreprise",
}

@router.post(
    "/",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Prédire l’attrition d’un employé",
    description=(
        "Calcule la probabilité d’attrition pour chaque entrée fournie.\n\n"
        "**Notes**\n"
        "- `model_name` doit référencer un modèle *actif* en base (`MLModel`).\n"
        "- Les données d’entrée sont persistées (`MLInput`) puis les sorties (`MLOutput`) sont enregistrées.\n"
        "- En cas d’erreur de features ou de prédiction, la requête retourne **400**.\n"
    ),
    responses={
        200: {"description": "Prédictions calculées avec succès."},
        400: {"description": "Erreur pendant la préparation des features ou la prédiction."},
        404: {"description": "Modèle introuvable ou inactif."},
        500: {"description": "Impossible de charger le modèle/erreur serveur."},
    },
)
def batch_predict(
    payload: PredictRequest = Body(
        ...,
        examples={
            "cas-minimal": {
                "summary": "Exemple minimal",
                "value": {
                    "model_name": "best_model",
                    "inputs": [
                        {
                            "id_employee": 123,
                            "age": 35,
                            "genre": "Homme",
                            "revenu_mensuel": 4200
                        }
                    ],
                },
            },
            "cas-complet": {
                "summary": "Exemple complet",
                "value": {
                    "model_name": "best_model",
                    "inputs": [
                        {
                            "id_employee": 123,
                            "age": 35,
                            "genre": "Homme",
                            "revenu_mensuel": 4200,
                            "statut_marital": "Célibataire",
                            "departement": "Ventes",
                            "poste": "Commercial",
                            "nombre_experiences_precedentes": 2,
                            "nombre_heures_travailless": 40,
                            "annee_experience_totale": 5,
                            "annees_dans_l_entreprise": 2,
                            "annees_dans_le_poste_actuel": 1,
                            "nombre_participation_pee": 1,
                            "nb_formations_suivies": 3,
                            "nombre_employee_sous_responsabilite": 0,
                            "code_sondage": 7,
                            "distance_domicile_travail": 12,
                            "niveau_education": 3,
                            "domaine_etude": "Marketing",
                            "ayant_enfants": "Non",
                            "frequence_deplacement": "Rarement",
                            "annees_depuis_la_derniere_promotion": 0,
                            "annes_sous_responsable_actuel": 1,
                            "satisfaction_employee_environnement": 3,
                            "note_evaluation_precedente": 4,
                            "niveau_hierarchique_poste": 2,
                            "satisfaction_employee_nature_travail": 3,
                            "satisfaction_employee_equipe": 4,
                            "satisfaction_employee_equilibre_pro_perso": 3,
                            "eval_number": "E2",
                            "note_evaluation_actuelle": 4,
                            "heure_supplementaires": "Non",
                            "augementation_salaire_precedente": 11
                        }
                    ],
                },
            },
        },
    ),
    db: Session = Depends(get_db),
):
    row = (
        db.query(MLModel)
        .filter(MLModel.name == payload.model_name)
        .first()
    )

    objs = [MLInput(**x.model_dump()) for x in payload.inputs]
    db.add_all(objs)
    db.commit()

    if not row or getattr(row, "is_active", True) is False:
        raise HTTPException(status_code=404, detail="Modèle introuvable ou inactif")

    try:
        m = load_model(payload.model_name)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chargement du modèle '{payload.model_name}' impossible: {e}",
        )

    try:
        df = pd.DataFrame([x.model_dump() for x in payload.inputs])
        X = compute_features(df)

        results: list[PredictItemResult] = []

        probas = m.predict_proba(X)
        classes = getattr(m, "classes_", None)

        for idx, p in enumerate(probas):
            i = int(p.argmax())
            key = str(classes[i]) if classes is not None else str(i)
            label = LABELS.get(key, key)

            pred = PredictItemResult(label=label, proba=float(p[i]))
            results.append(pred)

            db.add(
                MLOutput(
                    input_id=objs[idx].id,
                    prediction=label,
                    prob=float(p[i]),
                )
            )

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur pendant la prédiction: {e}")

    return PredictResponse(
        model_name=payload.model_name,
        results=results,
    )