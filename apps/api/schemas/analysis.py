from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class TrainingConfig(BaseModel):
    algorithm: Optional[str] = "RandomForestClassifier"
    random_state: Optional[int] = 42
    test_size: Optional[float] = 0.2
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="allow")

class FairnessConfig(BaseModel):
    target_column: str
    sensitive_attribute: str
    positive_label: Any
    metrics: List[str] = ["DemographicParity", "EqualOpportunity"]
    thresholds: Optional[Dict[str, float]] = Field(default_factory=dict)

class AnalysisConfig(BaseModel):
    schema_version: int = 1
    training: TrainingConfig
    fairness: FairnessConfig

class AnalysisConfigRequest(BaseModel):
    config: AnalysisConfig

class Recommendation(BaseModel):
    severity: str
    title: str
    description: str
    recommendedAction: str

class MetricResultResponse(BaseModel):
    metric_name: str
    metric_value: float
    subgroup: Optional[str] = None
    threshold: Optional[float] = None
    interpretation: Optional[str] = None

class AnalysisResponse(BaseModel):
    id: uuid.UUID
    dataset_version_id: uuid.UUID
    status: str
    config: AnalysisConfig
    metrics: List[MetricResultResponse] = []
    recommendations: List[Recommendation] = []
    feature_importance: List[dict] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DatasetVersionAnalyses(BaseModel):
    version_id: uuid.UUID
    storage_path: str
    created_at: datetime
    analyses: List[AnalysisResponse]

class DatasetAnalysesResponse(BaseModel):
    dataset_id: uuid.UUID
    versions: List[DatasetVersionAnalyses]
