from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.db import get_db
from models.ml import MLModel

router = APIRouter(tags=["Models"])


class MLModelOut(BaseModel):
    id: str = Field(..., description="Identifiant unique du modèle (UUID en chaîne).")
    name: str = Field(..., description="Nom court du modèle.")
    description: Optional[str] = Field(None, description="Description du modèle.")
    created_at: Optional[datetime] = Field(
        None, description="Date de création du modèle (UTC, ISO 8601)."
    )
    is_active: bool = Field(..., description="Modèle actif/inactif.")
    model_config = {"json_schema_extra": {
        "examples": [{
            "id": "5b1c7b3a-0000-4000-8000-000000000002",
            "name": "best_model",
            "description": "XGB v1",
            "created_at": "2025-09-15T10:11:03.950802+00:00",
            "is_active": True
        }]
    }}


@router.get(
    "/",
    response_model=List[MLModelOut],
    status_code=status.HTTP_200_OK,
    summary="Lister les modèles ML",
    description=(
        "Retourne la liste des modèles disponibles, triés du plus récent au plus ancien.\n\n"
        "**Remarques**\n"
        "- Les champs sont mappés depuis la table `ml_models`.\n"
    ),
    responses={
        200: {
            "description": "Liste des modèles.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "5b1c7b3a-0000-4000-8000-000000000002",
                            "name": "best_model",
                            "description": "XGB v1",
                            "created_at": "2025-09-15T10:11:03.950802+00:00",
                            "is_active": True
                        },
                        {
                            "id": "5b1c7b3a-0000-4000-8000-000000000001",
                            "name": "baseline",
                            "description": "Baseline model",
                            "created_at": "2025-09-15T10:11:03.950802+00:00",
                            "is_active": True
                        }
                    ]
                }
            },
        },
        500: {"description": "Erreur serveur lors de la lecture des modèles."},
    },
)
def list_ml_models(db: Session = Depends(get_db)) -> List[MLModelOut]:
    try:
        rows = (
            db.query(MLModel)
              .order_by(MLModel.created_at.desc())
              .all()
        )
        return [
            MLModelOut(
                id=str(r.id),
                name=r.name,
                description=r.description,
                created_at=r.created_at,
                is_active=r.is_active,
            )
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
