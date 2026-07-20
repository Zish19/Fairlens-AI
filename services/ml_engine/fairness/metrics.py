from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
import pandas as pd
import numpy as np

class MetricMetadata(BaseModel):
    name: str
    display_name: str
    description: str
    paper_reference: Optional[str] = None
    acceptable_range: Optional[str] = None
    supported_label_types: List[str] = ["binary"]

class MetricEvaluation(BaseModel):
    metric_name: str
    metric_value: float
    subgroup: Optional[str] = None
    threshold: Optional[float] = None
    interpretation: Optional[str] = None

class AnalysisResultSummary(BaseModel):
    metrics: List[MetricEvaluation]
    warnings: List[str] = []
    recommendations: List[dict] = []
    
    model_config = ConfigDict(from_attributes=True)

class Metric(ABC):
    @classmethod
    @abstractmethod
    def metadata(cls) -> MetricMetadata:
        """Returns metadata describing the metric."""
        pass
        
    @abstractmethod
    def supports(self, y_true: pd.Series, y_pred: pd.Series) -> bool:
        """Determines if this metric supports the provided data types."""
        pass
        
    @abstractmethod
    def evaluate(self, y_true: pd.Series, y_pred: pd.Series, sensitive_features: pd.Series) -> List[MetricEvaluation]:
        """
        Evaluates the metric and returns evaluations (potentially multiple if computing for subgroups).
        """
        pass
        
    @abstractmethod
    def interpret(self, evaluation: MetricEvaluation) -> str:
        """Provides a human-readable interpretation of a specific evaluation result."""
        pass
