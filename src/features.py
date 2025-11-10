import numpy as np
import pandas as pd

def _safe_div(a, b):
    a = pd.to_numeric(a, errors="coerce")
    b = pd.to_numeric(b, errors="coerce").replace(0, np.nan)
    return (a / b).fillna(0.0)

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    SAT_COLS = [
        "satisfaction_employee_environnement",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
    ]

    X = df.copy()
    X["sat_mean"] = X[SAT_COLS].astype(float).mean(axis=1)
    X["sat_std"]  = X[SAT_COLS].astype(float).std(axis=1, ddof=0)
    X["delta_eval"] = (
        X["note_evaluation_actuelle"].astype(float)
        - X["note_evaluation_precedente"].astype(float)
    )

    X["ratio_post_stab"]   = _safe_div(X["annes_sous_responsable_actuel"], X["annees_dans_le_poste_actuel"])
    X["revenu_par_niveau"] = _safe_div(X["revenu_mensuel"], X["niveau_hierarchique_poste"])

    age_bins      = [-np.inf, 25, 35, 45, 60, np.inf]
    dist_bins     = [-np.inf, 5, 10, 20, np.inf]
    revenu_bins   = [-np.inf, 2500, 4000, 6000, np.inf]
    sat_mean_bins = [-np.inf, 2.0, 3.0, 4.0, np.inf]

    X["tranche_age"]      = pd.cut(X["age"].astype(float), age_bins, labels=["<=25","26-35","36-45","46-60","60+"])
    X["tranche_distance"] = pd.cut(X["distance_domicile_travail"].astype(float), dist_bins, labels=["<=5","6-10","11-20",">20"])
    X["tranche_revenu"]   = pd.cut(X["revenu_mensuel"].astype(float), revenu_bins, labels=["<=2.5k","2.5-4k","4-6k",">6k"])
    X["tranche_sat_mean"] = pd.cut(X["sat_mean"], sat_mean_bins, labels=["basse","moyenne","bonne","excellente"])

    return X
