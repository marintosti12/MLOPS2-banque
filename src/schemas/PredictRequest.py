from typing import List
from pydantic import BaseModel

from schemas.ModelFeatures import ModelFeatures

class PredictRequest(BaseModel):
    model_name: str
    inputs: List[ModelFeatures]