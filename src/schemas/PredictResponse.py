from typing import List
from pydantic import BaseModel

from src.schemas.PredictItemResult import PredictItemResult


class PredictResponse(BaseModel):
    model_name: str
    results: List[PredictItemResult]