
from fastapi import FastAPI


from controllers.home_controller import router as ml_home_router
from controllers.predict_controller import router as predict_router


app = FastAPI(title="ML API",
    description="""
API d’inférence pour la prédiction d’attrition.
- **/predict**: prédire un résultat selon le modèle
- **/models**: lister les modèles disponibles
""", version="1.0.0")

app.include_router(ml_home_router)

app.include_router(predict_router)
