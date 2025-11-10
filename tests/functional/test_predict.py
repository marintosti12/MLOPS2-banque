from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from config.db import get_db

from models.ml import MLModel
from models.ml_inputs import MLInput
from models.ml_output import MLOutput

import uuid
from datetime import datetime, timezone


def test_simple_predict(tmp_path):
    db_path = tmp_path / "testing.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    SQLSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    MLModel.metadata.create_all(engine) 
    MLInput.metadata.create_all(engine) 
    MLOutput.metadata.create_all(engine) 

    session = SQLSession()

    def get_db_override():
        return session

    
    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app, raise_server_exceptions=False)

    created = datetime(2025, 9, 15, 10, 11, 3, 950802, tzinfo=timezone.utc)
    session.add_all(
        [
            MLModel(
                id=uuid.UUID("5b1c7b3a-0000-4000-8000-000000000001"),
                name="baseline",
                description="Baseline model",
                created_at=created,
                is_active=True,
            ),
            MLModel(
                id=uuid.UUID("5b1c7b3a-0000-4000-8000-000000000002"),
                name="best_model",
                description="XGB v1",
                created_at=created,
                is_active=True,
            ),
             MLModel(
                id=uuid.UUID("5b1c7b3a-0000-4000-8000-000000000003"),
                name="logistic_regression",
                description="Logistic Regression",
                created_at=created,
                is_active=True,
            ),
        ]
    )
    session.commit()


    payload = {
        "model_name": "best_model",
        "inputs": [{
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
        }]
    }

    
    resp = client.post("/predict", json=payload)

    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)

    app.dependency_overrides.clear()
    session.close()

    assert resp.status_code == 200
    data = resp.json()
    assert data["model_name"] == "best_model"
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1

    result = data["results"][0]
    assert result["label"] == "reste_dans_l_entreprise"
    assert isinstance(result["proba"], float)
    assert 0 <= result["proba"] <= 1


def test_not_found_model(tmp_path):
    db_path = tmp_path / "testing.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    SQLSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    MLModel.metadata.create_all(engine) 
    MLInput.metadata.create_all(engine) 
    MLOutput.metadata.create_all(engine) 

    session = SQLSession()

    def get_db_override():
        return session

    
    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app, raise_server_exceptions=False)

    created = datetime(2025, 9, 15, 10, 11, 3, 950802, tzinfo=timezone.utc)
    session.add_all(
        [
            MLModel(
                id=uuid.UUID("5b1c7b3a-0000-4000-8000-000000000001"),
                name="baseline",
                description="Baseline model",
                created_at=created,
                is_active=True,
            ),
        ]
    )
    session.commit()


    payload = {
        "model_name": "best_model",
        "inputs": [{
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
        }]
    }

    
    resp = client.post("/predict", json=payload)


    app.dependency_overrides.clear()
    session.close()

    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Modèle introuvable ou inactif"
    

def test_inactif_model(tmp_path):
    db_path = tmp_path / "testing.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    SQLSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    MLModel.metadata.create_all(engine) 
    MLInput.metadata.create_all(engine) 
    MLOutput.metadata.create_all(engine) 

    session = SQLSession()

    def get_db_override():
        return session

    
    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app, raise_server_exceptions=False)

    created = datetime(2025, 9, 15, 10, 11, 3, 950802, tzinfo=timezone.utc)
    session.add_all(
        [
            MLModel(
                id=uuid.UUID("5b1c7b3a-0000-4000-8000-000000000001"),
                name="baseline",
                description="Baseline model",
                created_at=created,
                is_active=False,
            ),
        ]
    )
    session.commit()


    payload = {
        "model_name": "baseline",
        "inputs": [{
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
        }]
    }

    
    resp = client.post("/predict", json=payload)

    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)

    app.dependency_overrides.clear()
    session.close()

    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Modèle introuvable ou inactif"
    

def test_list_models_returns_500_when_db_fails():
    class BrokenSession:
        def query(self, *a, **kw):
            raise RuntimeError("DB is down")

    def get_db_override():
        yield BrokenSession()

    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app, raise_server_exceptions=False)

    payload = {
        "model_name": "baseline",
        "inputs": [{
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
        }]
    }

    
    resp = client.post("/predict", json=payload)

    app.dependency_overrides.clear()

    assert resp.status_code == 500

