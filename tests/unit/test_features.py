import pandas as pd
import pytest
from features import compute_features

def test_compute_features_returns_matrix():
    df = pd.DataFrame([{"age": 35, "genre": "Homme", "revenu_mensuel": 4200, 
    "satisfaction_employee_environnement": 3,
    "satisfaction_employee_nature_travail": 3,
    "satisfaction_employee_equipe": 3,
    "satisfaction_employee_equilibre_pro_perso": 3, "note_evaluation_actuelle": 2, 'note_evaluation_precedente' : 3, "annes_sous_responsable_actuel" : 2, "annees_dans_le_poste_actuel" : 4, "niveau_hierarchique_poste": 2, "distance_domicile_travail" : 5}])
    X = compute_features(df)
    assert hasattr(X, "shape")
    assert X.shape[0] == 1 

def test_compute_features_raises_on_empty():
    with pytest.raises(Exception):
        compute_features(pd.DataFrame())
