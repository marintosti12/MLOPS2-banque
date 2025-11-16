from pydantic import BaseModel, Field

class PredictItemResult(BaseModel):
    label: str = Field(..., description="Libellé prédit (classe).")
    proba: float = Field(..., ge=0.0, le=1.0, description="Probabilité associée à la classe prédite.")
