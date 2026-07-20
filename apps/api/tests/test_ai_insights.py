from services.ml_engine.insights.builder import InsightBuilder
from services.ml_engine.insights.ai_service import get_ai_service

class MockAnalysis:
    def __init__(self):
        self.id = "1234-abcd"
        self.dataset_version_id = "5678-efgh"
        self.config = {
            "fairness": {
                "target_column": "income",
                "sensitive_attribute": "sex",
                "positive_label": "1"
            }
        }
        self.status = "COMPLETED"
        self.metrics = []
        self.feature_importance = [
            {"feature": "age", "importance": 0.5, "rank": 1},
            {"feature": "education", "importance": 0.3, "rank": 2}
        ]
        self.recommendations = [
            {"severity": "warning", "title": "Test Rec", "recommendedAction": "Action"}
        ]

def test_insight_builder_no_raw_data():
    mock_analysis = MockAnalysis()
    context = InsightBuilder.build_context(mock_analysis)
    
    # Assert deterministic context creation
    assert context.analysis_id == "1234-abcd"
    assert context.dataset.target_column == "income"
    assert len(context.explainability.top_features) == 2
    
    # Assert no raw dataframes or matrices exist in context dict
    context_dict = context.model_dump()
    context_str = str(context_dict)
    
    assert "DataFrame" not in context_str
    assert "Series" not in context_str
    assert "tensor" not in context_str

def test_ai_stub_provider_determinism():
    mock_analysis = MockAnalysis()
    context = InsightBuilder.build_context(mock_analysis)
    
    ai_service = get_ai_service()
    insight1 = ai_service.generate_insights(context)
    insight2 = ai_service.generate_insights(context)
    
    # Assert deterministic outputs
    assert insight1.model_dump() == insight2.model_dump()
    
    # Assert expected fields
    assert "income" in insight1.summary
    assert "sex" in insight1.summary
    assert "age" in insight1.explainability_findings[0]
    assert len(insight1.recommendations) > 0
    assert len(insight1.follow_up_questions) > 0
