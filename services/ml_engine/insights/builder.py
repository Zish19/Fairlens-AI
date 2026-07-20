from typing import Any
from .schemas import InsightContext, DatasetSummary, FairnessSummary, ExplainabilitySummaryContext

class InsightBuilder:
    @staticmethod
    def build_context(analysis: Any) -> InsightContext:
        """
        Builds the structured InsightContext from an Analysis ORM object.
        Ensures no raw dataframes or PII are passed to the AI service.
        """
        config = analysis.config
        
        dataset_summary = DatasetSummary(
            version_id=str(analysis.dataset_version_id),
            target_column=config.get("fairness", {}).get("target_column", ""),
            sensitive_attribute=config.get("fairness", {}).get("sensitive_attribute", ""),
            positive_label=str(config.get("fairness", {}).get("positive_label", ""))
        )
        
        # Extract metrics
        # The metrics are stored in analysis.metrics, but we can query them or 
        # assume they are available if loaded via relationship, but in FastAPI router 
        # it might be easier to pass them or fetch them.
        # Let's assume we pass the ORM object which has metrics loaded.
        metrics_list = []
        for m in getattr(analysis, "metrics", []):
            metrics_list.append({
                "metric_name": m.metric_name,
                "metric_value": m.metric_value,
                "subgroup": m.subgroup,
                "interpretation": m.interpretation
            })
            
        fairness_summary = FairnessSummary(metrics=metrics_list)
        
        # Feature importance (top 10 to keep prompt small)
        fi = analysis.feature_importance or []
        # sort just in case, though they should be sorted
        fi_sorted = sorted(fi, key=lambda x: x.get("importance", 0), reverse=True)
        top_features = fi_sorted[:10]
        explainability_summary = ExplainabilitySummaryContext(top_features=top_features)
        
        return InsightContext(
            analysis_id=str(analysis.id),
            dataset=dataset_summary,
            fairness=fairness_summary,
            explainability=explainability_summary,
            recommendations=analysis.recommendations or [],
            warnings=[],
            metadata={"status": analysis.status}
        )
