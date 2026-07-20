import shap
import pandas as pd
import numpy as np
import logging
from typing import List, Tuple

from .schemas import FeatureImportance, GlobalExplanation

logger = logging.getLogger(__name__)

class ShapAdapter:
    @staticmethod
    def compute_global_importance(model, X_test: pd.DataFrame) -> GlobalExplanation:
        """
        Computes the global feature importance using SHAP values.
        Returns a sorted list of FeatureImportance objects.
        """
        try:
            # For most scikit-learn tree-based models, TreeExplainer is best.
            # We attempt TreeExplainer first, fallback to KernelExplainer if needed.
            try:
                explainer = shap.TreeExplainer(model)
                # Ensure we only use numeric data or acceptable types for SHAP
                # SHAP might require arrays, but pandas dataframes are usually fine.
                shap_values = explainer.shap_values(X_test)
            except Exception as e:
                logger.warning(f"TreeExplainer failed, falling back to KernelExplainer: {e}")
                # Use a small background dataset for KernelExplainer to save time
                background = shap.kmeans(X_test, 10)
                explainer = shap.KernelExplainer(model.predict_proba, background)
                shap_values = explainer.shap_values(X_test)

            # shap_values can be a list for multi-class or a numpy array
            if isinstance(shap_values, list):
                # For binary classification (common case), class 1 is usually index 1
                shap_vals = shap_values[1]
            elif len(shap_values.shape) == 3:
                 # shap_values shape (n_samples, n_features, n_classes)
                 shap_vals = shap_values[:, :, 1]
            else:
                shap_vals = shap_values

            # Calculate mean absolute SHAP values per feature
            mean_abs_shap = np.abs(shap_vals).mean(axis=0)

            # Map to feature names
            features = X_test.columns.tolist()
            importance_pairs = list(zip(features, mean_abs_shap))
            
            # Sort descending
            importance_pairs.sort(key=lambda x: x[1], reverse=True)

            feature_importance_list = [
                FeatureImportance(
                    feature=feat,
                    importance=float(imp),
                    rank=i + 1
                )
                for i, (feat, imp) in enumerate(importance_pairs)
            ]

            return GlobalExplanation(feature_importance=feature_importance_list)

        except Exception as e:
            logger.error(f"Error computing SHAP values: {e}")
            return GlobalExplanation(feature_importance=[])
