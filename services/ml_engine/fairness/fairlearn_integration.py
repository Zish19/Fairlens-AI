import pandas as pd
from typing import List
from sklearn.metrics import recall_score
from fairlearn.metrics import MetricFrame, demographic_parity_difference, equal_opportunity_difference, selection_rate

from services.ml_engine.fairness.metrics import Metric, MetricMetadata, MetricEvaluation
from services.ml_engine.fairness.registry import MetricRegistry

# Global registry instance
registry = MetricRegistry()

class DemographicParity(Metric):
    @classmethod
    def metadata(cls) -> MetricMetadata:
        return MetricMetadata(
            name="DemographicParity",
            display_name="Demographic Parity Difference",
            description="Measures the difference in selection rates across groups.",
            paper_reference="Dwork et al., 2011",
            acceptable_range="[-0.1, 0.1]",
            supported_label_types=["binary"]
        )
        
    def supports(self, y_true: pd.Series, y_pred: pd.Series) -> bool:
        return set(y_pred.unique()).issubset({0, 1})
        
    def evaluate(self, y_true: pd.Series, y_pred: pd.Series, sensitive_features: pd.Series) -> List[MetricEvaluation]:
        diff = demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive_features)
        
        mf = MetricFrame(
            metrics=selection_rate,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features
        )
        
        evals = []
        base_eval = MetricEvaluation(
            metric_name="DemographicParityDifference",
            metric_value=diff
        )
        base_eval.interpretation = self.interpret(base_eval)
        evals.append(base_eval)
        
        for group, rate in mf.by_group.items():
            evals.append(MetricEvaluation(
                metric_name="SelectionRate",
                metric_value=rate,
                subgroup=str(group)
            ))
            
        return evals

    def interpret(self, evaluation: MetricEvaluation) -> str:
        if abs(evaluation.metric_value) <= 0.1:
            return "Passes demographic parity. The difference in selection rates is within the acceptable 10% margin."
        return f"Fails demographic parity. The difference of {evaluation.metric_value:.3f} indicates potential bias."


class EqualOpportunity(Metric):
    @classmethod
    def metadata(cls) -> MetricMetadata:
        return MetricMetadata(
            name="EqualOpportunity",
            display_name="Equal Opportunity Difference",
            description="Measures the difference in true positive rates (recall) across groups.",
            paper_reference="Hardt et al., 2016",
            acceptable_range="[-0.1, 0.1]",
            supported_label_types=["binary"]
        )
        
    def supports(self, y_true: pd.Series, y_pred: pd.Series) -> bool:
        return set(y_true.unique()).issubset({0, 1}) and set(y_pred.unique()).issubset({0, 1})
        
    def evaluate(self, y_true: pd.Series, y_pred: pd.Series, sensitive_features: pd.Series) -> List[MetricEvaluation]:
        diff = equal_opportunity_difference(y_true, y_pred, sensitive_features=sensitive_features)
        
        mf = MetricFrame(
            metrics=recall_score,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features
        )
        
        evals = []
        base_eval = MetricEvaluation(
            metric_name="EqualOpportunityDifference",
            metric_value=diff
        )
        base_eval.interpretation = self.interpret(base_eval)
        evals.append(base_eval)
        
        for group, rate in mf.by_group.items():
            evals.append(MetricEvaluation(
                metric_name="TruePositiveRate",
                metric_value=rate,
                subgroup=str(group)
            ))
            
        return evals

    def interpret(self, evaluation: MetricEvaluation) -> str:
        if abs(evaluation.metric_value) <= 0.1:
            return "Passes equal opportunity. True positive rates are relatively equal."
        return f"Fails equal opportunity. The true positive rate difference is {evaluation.metric_value:.3f}."

# Register the metrics
registry.register(DemographicParity)
registry.register(EqualOpportunity)
