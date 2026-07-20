import pandas as pd
from typing import Dict, Any, List
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from apps.api.schemas.analysis import AnalysisConfig
from services.ml_engine.fairness.fairlearn_integration import registry
from services.ml_engine.fairness.metrics import AnalysisResultSummary, MetricEvaluation

class FairnessService:
    def __init__(self, config: AnalysisConfig):
        self.config = config
        
    def _train_model(self, df: pd.DataFrame, target_col: str):
        # Convert target to numerical binary explicitly for sklearn
        y = df[target_col].astype(int)
        X = df.drop(columns=[target_col])
        
        # Keep only numeric columns for MVP simplicity (or one-hot encode)
        # One-hot encoding string columns
        categorical_cols = X.select_dtypes(include=['object', 'string', 'category']).columns
        X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
        
        # Fill NaNs
        X = X.fillna(0)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.training.test_size, random_state=self.config.training.random_state
        )
        
        model = RandomForestClassifier(random_state=self.config.training.random_state)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        return X_test, y_test, pd.Series(y_pred, index=X_test.index), model

    def analyze(self, df: pd.DataFrame) -> tuple[AnalysisResultSummary, Any, pd.DataFrame]:
        target_col = self.config.fairness.target_column
        sensitive_col = self.config.fairness.sensitive_attribute
        
        if target_col not in df.columns or sensitive_col not in df.columns:
            return AnalysisResultSummary(
                metrics=[],
                warnings=[f"Target or sensitive column missing from dataset."]
            ), None, None
            
        sensitive_features = df[sensitive_col].copy()
        
        pos_label = self.config.fairness.positive_label
        
        df_eval = df.copy()
        df_eval[target_col] = (df_eval[target_col] == pos_label).astype(int)
        
        X_test, y_test, y_pred, model = self._train_model(df_eval, target_col)
        
        sensitive_test = sensitive_features.loc[X_test.index]
        
        evaluations: List[MetricEvaluation] = []
        warnings: List[str] = []
        
        for metric_name in self.config.fairness.metrics:
            try:
                MetricClass = registry.get(metric_name)
                metric_instance = MetricClass()
                
                if metric_instance.supports(y_test, y_pred):
                    evals = metric_instance.evaluate(y_test, y_pred, sensitive_test)
                    evaluations.extend(evals)
                else:
                    warnings.append(f"Metric {metric_name} does not support the provided data types.")
            except Exception as e:
                warnings.append(f"Error evaluating {metric_name}: {str(e)}")
                
        return AnalysisResultSummary(
            metrics=evaluations,
            warnings=warnings,
            recommendations=[
                {
                    "severity": "warning",
                    "title": "Potential demographic disparity",
                    "description": "The metric differences might be above standard thresholds.",
                    "recommendedAction": "Review model configurations or consider mitigation algorithms if disparities exist."
                }
            ] if evaluations else []
        ), model, X_test
