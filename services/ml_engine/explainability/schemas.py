from pydantic import BaseModel, Field
from typing import List

class FeatureImportance(BaseModel):
    feature: str
    importance: float
    rank: int

class GlobalExplanation(BaseModel):
    feature_importance: List[FeatureImportance] = Field(default_factory=list)

class ExplainabilitySummary(BaseModel):
    global_explanation: GlobalExplanation
