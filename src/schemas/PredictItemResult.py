from typing import Optional
from pydantic import BaseModel


class PredictItemResult(BaseModel):
    label: str
    proba: Optional[float] = None
