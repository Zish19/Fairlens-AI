import pandas as pd
import numpy as np
from typing import Dict, List, Optional

from services.ml_engine.schemas import (
    ProfileSummary,
    NumericSummary,
    CategoricalSummary,
    MissingValueSummary,
    CorrelationSummary,
    ClassBalanceSummary
)

def missing_values(series: pd.Series) -> MissingValueSummary:
    count = int(series.isna().sum())
    percentage = float(count / len(series)) if len(series) > 0 else 0.0
    return MissingValueSummary(count=count, percentage=percentage)

def duplicates(df: pd.DataFrame) -> int:
    return int(df.duplicated().sum())

def numeric_summary(series: pd.Series) -> NumericSummary:
    # Drop NAs for statistics
    s = series.dropna()
    if s.empty:
        return NumericSummary(
            mean=0.0, std=0.0, min=0.0, max=0.0,
            p25=0.0, p50=0.0, p75=0.0,
            missing=missing_values(series)
        )
        
    return NumericSummary(
        mean=float(s.mean()),
        std=float(s.std()) if len(s) > 1 else 0.0,
        min=float(s.min()),
        max=float(s.max()),
        p25=float(s.quantile(0.25)),
        p50=float(s.median()),
        p75=float(s.quantile(0.75)),
        missing=missing_values(series)
    )

def categorical_summary(series: pd.Series) -> CategoricalSummary:
    s = series.dropna()
    unique_count = int(s.nunique())
    
    top_cat = None
    top_freq = None
    if not s.empty:
        counts = s.value_counts()
        if not counts.empty:
            top_cat = str(counts.index[0])
            top_freq = int(counts.iloc[0])
            
    return CategoricalSummary(
        unique_count=unique_count,
        top_category=top_cat,
        top_frequency=top_freq,
        missing=missing_values(series)
    )

def correlation(df: pd.DataFrame) -> CorrelationSummary:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return CorrelationSummary(matrix={})
        
    corr_matrix = numeric_df.corr().fillna(0).to_dict()
    return CorrelationSummary(matrix=corr_matrix)

def class_balance(series: pd.Series) -> ClassBalanceSummary:
    s = series.dropna()
    counts = s.value_counts().to_dict()
    total = sum(counts.values())
    percentages = {str(k): float(v / total) for k, v in counts.items()} if total > 0 else {}
    
    return ClassBalanceSummary(
        class_counts={str(k): int(v) for k, v in counts.items()},
        class_percentages=percentages
    )

def profile(df: pd.DataFrame, target_columns: Optional[List[str]] = None) -> ProfileSummary:
    """
    Orchestrates the entire profiling process over the DataFrame.
    Returns a typed ProfileSummary model.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    
    dupe_count = duplicates(df)
    dupe_pct = float(dupe_count / total_rows) if total_rows > 0 else 0.0
    
    numeric_features = {}
    categorical_features = {}
    
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_features[str(col)] = numeric_summary(df[col])
        else:
            categorical_features[str(col)] = categorical_summary(df[col])
            
    corr_sum = correlation(df)
    
    balance_dict = {}
    if target_columns:
        for col in target_columns:
            if col in df.columns:
                balance_dict[col] = class_balance(df[col])
                
    return ProfileSummary(
        total_rows=total_rows,
        total_columns=total_cols,
        duplicates_count=dupe_count,
        duplicates_percentage=dupe_pct,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        correlations=corr_sum,
        class_balance=balance_dict if balance_dict else None
    )
