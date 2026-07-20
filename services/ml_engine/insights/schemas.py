from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# InsightContext (Input to AI Service)

class DatasetSummary(BaseModel):
    version_id: str
    target_column: str
    sensitive_attribute: str
    positive_label: str

class FairnessSummary(BaseModel):
    metrics: List[Dict[str, Any]]

class ExplainabilitySummaryContext(BaseModel):
    top_features: List[Dict[str, Any]]

class InsightContext(BaseModel):
    analysis_id: str
    dataset: DatasetSummary
    fairness: FairnessSummary
    explainability: ExplainabilitySummaryContext
    recommendations: List[Dict[str, Any]]
    warnings: List[str]
    metadata: Dict[str, Any]

# InsightResponse (Output from AI Service)

class InsightResponse(BaseModel):
    summary: str
    strengths: List[str]
    risks: List[str]
    fairness_findings: List[str]
    explainability_findings: List[str]
    recommendations: List[str]
    follow_up_questions: List[str]
