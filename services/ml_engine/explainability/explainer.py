from .schemas import ExplainabilitySummary
from .shap_adapter import ShapAdapter
import pandas as pd

class ExplainerService:
    @staticmethod
    def explain_model(model, X_test: pd.DataFrame) -> ExplainabilitySummary:
        """
        Orchestrates explainability logic, returning a deterministic summary.
        """
        global_exp = ShapAdapter.compute_global_importance(model, X_test)
        return ExplainabilitySummary(global_explanation=global_exp)
