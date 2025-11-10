import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from huggingface_hub import hf_hub_download
import joblib

HF_REPO_ID  = os.getenv("HF_REPO_ID",  "Marintosti/attrition")
HF_TOKEN    = os.getenv("HF_TOKEN")      

ENV: Literal["dev", "test", "prod"] = os.getenv("APP_ENV", "dev").lower()
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))

def _load_local(name: str) -> Any:
    path = ARTIFACTS_DIR / f"{name}.joblib"
    if not path.exists():
        raise FileNotFoundError(
            f"Modèle local introuvable: {path}. "
        )
    return joblib.load(path)

@lru_cache(maxsize=1)
def load_model(name) -> Any:

    if ENV in ("dev"):
        return _load_local(name)
     
    hf_path = hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=f"{name}.joblib",
        token=HF_TOKEN,
        local_files_only=False,
    )

    return joblib.load(hf_path)
