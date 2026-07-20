from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, List, Optional

class MissingValueSummary(BaseModel):
    count: int
    percentage: float

class NumericSummary(BaseModel):
    mean: float
    std: float
    min: float
    max: float
    p25: float
    p50: float
    p75: float
    missing: MissingValueSummary

class CategoricalSummary(BaseModel):
    unique_count: int
    top_category: Optional[str]
    top_frequency: Optional[int]
    missing: MissingValueSummary

class CorrelationSummary(BaseModel):
    matrix: Dict[str, Dict[str, float]]

class ClassBalanceSummary(BaseModel):
    class_counts: Dict[str, int]
    class_percentages: Dict[str, float]

class ProfileSummary(BaseModel):
    total_rows: int
    total_columns: int
    duplicates_count: int
    duplicates_percentage: float
    numeric_features: Dict[str, NumericSummary]
    categorical_features: Dict[str, CategoricalSummary]
    correlations: Optional[CorrelationSummary] = None
    class_balance: Optional[Dict[str, ClassBalanceSummary]] = None

    model_config = ConfigDict(from_attributes=True)
