import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from services.ml_engine.explainability.shap_adapter import ShapAdapter

def test_shap_global_importance():
    # Create simple dataset
    X_train = pd.DataFrame({
        "feat1": np.random.rand(100),
        "feat2": np.random.randint(0, 2, 100)
    })
    y_train = (X_train["feat1"] > 0.5).astype(int)
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    
    X_test = pd.DataFrame({
        "feat1": np.random.rand(20),
        "feat2": np.random.randint(0, 2, 20)
    })
    
    global_exp = ShapAdapter.compute_global_importance(model, X_test)
    
    # Assertions
    assert len(global_exp.feature_importance) == 2
    # feat1 should be most important because it perfectly predicts the target
    assert global_exp.feature_importance[0].feature == "feat1"
    assert global_exp.feature_importance[0].rank == 1
    assert global_exp.feature_importance[1].feature == "feat2"
    assert global_exp.feature_importance[1].rank == 2

def test_shap_constant_feature():
    X_train = pd.DataFrame({
        "feat1": np.random.rand(100),
        "constant_feat": np.zeros(100)
    })
    y_train = (X_train["feat1"] > 0.5).astype(int)
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    
    X_test = pd.DataFrame({
        "feat1": np.random.rand(20),
        "constant_feat": np.zeros(20)
    })
    
    global_exp = ShapAdapter.compute_global_importance(model, X_test)
    
    assert len(global_exp.feature_importance) == 2
    # constant feature should have 0 importance
    constant_fi = next(fi for fi in global_exp.feature_importance if fi.feature == "constant_feat")
    assert np.isclose(constant_fi.importance, 0.0, atol=1e-5)
