# src/features.py
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
    
    if 'CNT_CHILDREN' in df.columns and 'CNT_FAM_MEMBERS' in df.columns:
        df['CHILDREN_RATIO'] = safe_div(df['CNT_CHILDREN'], df['CNT_FAM_MEMBERS'])
    
    if 'AMT_INCOME_TOTAL' in df.columns and 'CNT_FAM_MEMBERS' in df.columns:
        df['INCOME_PER_PERSON'] = safe_div(df['AMT_INCOME_TOTAL'], df['CNT_FAM_MEMBERS'])
    
    if 'DAYS_BIRTH' in df.columns:
        df['AGE'] = -df['DAYS_BIRTH'] / 365.25
        if 'CNT_FAM_MEMBERS' in df.columns:
            df['AGE_PER_MEMBER'] = safe_div(df['AGE'], df['CNT_FAM_MEMBERS'])
    
    if 'DAYS_EMPLOYED' in df.columns and 'DAYS_BIRTH' in df.columns:
        df['DAYS_EMPLOYED_PERC'] = safe_div(df['DAYS_EMPLOYED'], df['DAYS_BIRTH'])
    
    if 'AMT_INCOME_TOTAL' in df.columns and 'AMT_CREDIT' in df.columns:
        df['INCOME_CREDIT_PERC'] = safe_div(df['AMT_INCOME_TOTAL'], df['AMT_CREDIT'])
    
    if 'AMT_ANNUITY' in df.columns and 'AMT_INCOME_TOTAL' in df.columns:
        df['ANNUITY_INCOME_PERC'] = safe_div(df['AMT_ANNUITY'], df['AMT_INCOME_TOTAL'])
    
    if 'AMT_ANNUITY' in df.columns and 'AMT_CREDIT' in df.columns:
        df['PAYMENT_RATE'] = safe_div(df['AMT_ANNUITY'], df['AMT_CREDIT'])
    

    num_cols_to_fill = df.select_dtypes(include=['number']).columns.tolist()
    df[num_cols_to_fill] = df[num_cols_to_fill].fillna(0)
    
    cat_cols_to_fill = df.select_dtypes(include=['object', 'category']).columns.tolist()
    for c in cat_cols_to_fill:
        mode_val = df[c].mode(dropna=True)
        fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
        df[c] = df[c].fillna(fill_val)
    
    cat_cols = [
        'NAME_CONTRACT_TYPE',
        'CODE_GENDER',
        'FLAG_OWN_CAR',
        'FLAG_OWN_REALTY',
        'NAME_TYPE_SUITE',
        'NAME_INCOME_TYPE',
        'NAME_EDUCATION_TYPE',
        'NAME_FAMILY_STATUS',
        'NAME_HOUSING_TYPE',
        'OCCUPATION_TYPE',
        'WEEKDAY_APPR_PROCESS_START',
        'ORGANIZATION_TYPE',
        'FONDKAPREMONT_MODE',
        'HOUSETYPE_MODE',
        'WALLSMATERIAL_MODE',
        'EMERGENCYSTATE_MODE',
        'CNT_CHILDREN_BIN'
    ]
    
    num_cols = [
        'SK_ID_CURR',
        'CNT_CHILDREN',
        'AMT_INCOME_TOTAL',
        'AMT_CREDIT',
        'AMT_ANNUITY',
        'AMT_GOODS_PRICE',
        'REGION_POPULATION_RELATIVE',
        'DAYS_BIRTH',
        'DAYS_EMPLOYED',
        'DAYS_REGISTRATION',
        'DAYS_ID_PUBLISH',
        'OWN_CAR_AGE',
        'FLAG_MOBIL',
        'FLAG_EMP_PHONE',
        'FLAG_WORK_PHONE',
        'FLAG_CONT_MOBILE',
        'FLAG_PHONE',
        'FLAG_EMAIL',
        'CNT_FAM_MEMBERS',
        'REGION_RATING_CLIENT',
        'REGION_RATING_CLIENT_W_CITY',
        'HOUR_APPR_PROCESS_START',
        'REG_REGION_NOT_LIVE_REGION',
        'REG_REGION_NOT_WORK_REGION',
        'LIVE_REGION_NOT_WORK_REGION',
        'REG_CITY_NOT_LIVE_CITY',
        'REG_CITY_NOT_WORK_CITY',
        'LIVE_CITY_NOT_WORK_CITY',
        'EXT_SOURCE_1',
        'EXT_SOURCE_2',
        'EXT_SOURCE_3',
        'APARTMENTS_AVG',
        'BASEMENTAREA_AVG',
        'YEARS_BEGINEXPLUATATION_AVG',
        'YEARS_BUILD_AVG',
        'COMMONAREA_AVG',
        'ELEVATORS_AVG',
        'ENTRANCES_AVG',
        'FLOORSMAX_AVG',
        'FLOORSMIN_AVG',
        'LANDAREA_AVG',
        'LIVINGAPARTMENTS_AVG',
        'LIVINGAREA_AVG',
        'NONLIVINGAPARTMENTS_AVG',
        'NONLIVINGAREA_AVG',
        'TOTALAREA_MODE',
        'OBS_30_CNT_SOCIAL_CIRCLE',
        'DEF_30_CNT_SOCIAL_CIRCLE',
        'OBS_60_CNT_SOCIAL_CIRCLE',
        'DEF_60_CNT_SOCIAL_CIRCLE',
        'DAYS_LAST_PHONE_CHANGE',
        'FLAG_DOCUMENT_2',
        'FLAG_DOCUMENT_3',
        'FLAG_DOCUMENT_4',
        'FLAG_DOCUMENT_5',
        'FLAG_DOCUMENT_6',
        'FLAG_DOCUMENT_7',
        'FLAG_DOCUMENT_8',
        'FLAG_DOCUMENT_9',
        'FLAG_DOCUMENT_10',
        'FLAG_DOCUMENT_11',
        'FLAG_DOCUMENT_12',
        'FLAG_DOCUMENT_13',
        'FLAG_DOCUMENT_14',
        'FLAG_DOCUMENT_15',
        'FLAG_DOCUMENT_16',
        'FLAG_DOCUMENT_17',
        'FLAG_DOCUMENT_18',
        'FLAG_DOCUMENT_19',
        'FLAG_DOCUMENT_20',
        'FLAG_DOCUMENT_21',
        'AMT_REQ_CREDIT_BUREAU_HOUR',
        'AMT_REQ_CREDIT_BUREAU_DAY',
        'AMT_REQ_CREDIT_BUREAU_WEEK',
        'AMT_REQ_CREDIT_BUREAU_MON',
        'AMT_REQ_CREDIT_BUREAU_QRT',
        'AMT_REQ_CREDIT_BUREAU_YEAR',
        'nb_loans',
        'sum_debt',
        'AGE',
        'CHILDREN_RATIO',
        'INCOME_PER_PERSON',
        'AGE_PER_MEMBER',
        'DAYS_EMPLOYED_PERC',
        'INCOME_CREDIT_PERC',
        'ANNUITY_INCOME_PERC',
        'PAYMENT_RATE'
    ]
    
    all_cols = num_cols + cat_cols
    missing_cols = [c for c in all_cols if c not in df.columns]
    
    if missing_cols:
        for c in missing_cols:
            if c in cat_cols:
                df[c] = "Unknown"
            else:
                df[c] = 0
    
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
    
    df_final = df[all_cols]
    
    return df_final