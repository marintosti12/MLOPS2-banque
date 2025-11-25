import pandas as pd
import numpy as np

def safe_div(a, b):
    return np.where(b == 0, 0, a / b)


def compute_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
  
    if 'DAYS_EMPLOYED' in df.columns:
        df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace(365243, np.nan)
    
    to_drop = [
        'COMMONAREA_MODE', 'COMMONAREA_MEDI',
        'NONLIVINGAPARTMENTS_MODE', 'NONLIVINGAPARTMENTS_MEDI',
        'LIVINGAPARTMENTS_MODE', 'LIVINGAPARTMENTS_MEDI',
        'FLOORSMIN_MODE', 'FLOORSMIN_MEDI',
        'YEARS_BUILD_MODE', 'YEARS_BUILD_MEDI',
        'LANDAREA_MODE', 'LANDAREA_MEDI',
        'BASEMENTAREA_MODE', 'BASEMENTAREA_MEDI',
        'ELEVATORS_MODE', 'ELEVATORS_MEDI'
    ]
    df = df.drop(columns=[c for c in to_drop if c in df.columns])
    
    isna_cols = [
        'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'OWN_CAR_AGE',
        'COMMONAREA_AVG', 'NONLIVINGAPARTMENTS_AVG', 'LIVINGAPARTMENTS_AVG',
        'FLOORSMIN_AVG', 'YEARS_BUILD_AVG', 'LANDAREA_AVG', 'BASEMENTAREA_AVG',
        'NONLIVINGAREA_AVG', 'ELEVATORS_AVG', 'FONDKAPREMONT_MODE'
    ]
    for c in isna_cols:
        if c in df.columns:
            df[c + "_ISNA"] = df[c].isna().astype(int)
    

    df['CHILDREN_RATIO'] = safe_div(df['CNT_CHILDREN'], df['CNT_FAM_MEMBERS'])
    df['INCOME_PER_PERSON'] = safe_div(df['AMT_INCOME_TOTAL'], df['CNT_FAM_MEMBERS'])
    
    df['AGE'] = -df['DAYS_BIRTH'] / 365.25
    df['AGE_PER_MEMBER'] = safe_div(df['AGE'], df['CNT_FAM_MEMBERS'])
    
    df['DAYS_EMPLOYED_PERC'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']
    df['INCOME_CREDIT_PERC'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']
    df['ANNUITY_INCOME_PERC'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']
    df['PAYMENT_RATE'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']
    
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    if num_cols:
        med = df[num_cols].median()
        df[num_cols] = df[num_cols].fillna(med)
    
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    for c in cat_cols:
        if df[c].notna().any():
            mode_val = df[c].mode(dropna=True)
            fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
        else:
            fill_val = "Unknown"
        df[c] = df[c].fillna(fill_val)
    
    return df