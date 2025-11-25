
import os
from fastapi import FastAPI


from src.controllers.home_controller import router as ml_home_router
from src.controllers.predict_controller import router as predict_router
from src.middleware.profiling import ProfilingMiddleware


app = FastAPI(title="ML API",
    description="""
API d’inférence pour la prédiction d’attrition.
- **/predict**: prédire un résultat selon le modèle
- **/models**: lister les modèles disponibles
""", version="1.0.0")

PROFILING_ENABLED = os.getenv("PROFILING_ENABLED", "false").lower() == "true"

if PROFILING_ENABLED:
    app.add_middleware(
        ProfilingMiddleware, 
        enabled=True,
    )

app.include_router(ml_home_router)

app.include_router(predict_router)
