import pandas as pd
import numpy as np
from services.ml_engine.profiling import (
    missing_values,
    duplicates,
    numeric_summary,
    categorical_summary,
    correlation,
    class_balance,
    profile
)

def test_missing_values():
    s = pd.Series([1, np.nan, 3, np.nan])
    res = missing_values(s)
    assert res.count == 2
    assert res.percentage == 0.5


def test_duplicates():
    df = pd.DataFrame({"A": [1, 2, 2, 3], "B": ["x", "y", "y", "z"]})
    assert duplicates(df) == 1


def test_numeric_summary():
    s = pd.Series([1, 2, 3, 4, 5, np.nan])
    res = numeric_summary(s)
    assert res.mean == 3.0
    assert res.min == 1.0
    assert res.max == 5.0
    assert res.missing.count == 1
    
    # Empty numeric test
    empty_s = pd.Series([np.nan, np.nan])
    empty_res = numeric_summary(empty_s)
    assert empty_res.mean == 0.0


def test_categorical_summary():
    s = pd.Series(["apple", "banana", "apple", "cherry", np.nan])
    res = categorical_summary(s)
    assert res.unique_count == 3
    assert res.top_category == "apple"
    assert res.top_frequency == 2
    assert res.missing.count == 1


def test_correlation():
    df = pd.DataFrame({
        "A": [1, 2, 3, 4],
        "B": [2, 4, 6, 8],
        "C": [10, 8, 6, 4]
    })
    res = correlation(df)
    # A & B perfectly positively correlated
    assert np.isclose(res.matrix["A"]["B"], 1.0)
    # A & C perfectly negatively correlated
    assert np.isclose(res.matrix["A"]["C"], -1.0)


def test_class_balance():
    s = pd.Series(["cat", "dog", "cat"])
    res = class_balance(s)
    assert res.class_counts["cat"] == 2
    assert res.class_counts["dog"] == 1
    assert np.isclose(res.class_percentages["cat"], 0.6666, atol=1e-3)


def test_profile_orchestrator():
    df = pd.DataFrame({
        "age": [25, 30, 35, 40, np.nan],
        "gender": ["M", "F", "F", "M", "M"],
        "income": [50000, 60000, 70000, 80000, 50000]
    })
    
    res = profile(df, target_columns=["gender"])
    
    assert res.total_rows == 5
    assert res.total_columns == 3
    assert res.duplicates_count == 0
    assert "age" in res.numeric_features
    assert "income" in res.numeric_features
    assert "gender" in res.categorical_features
    
    assert res.numeric_features["age"].missing.count == 1
    assert res.categorical_features["gender"].top_category == "M"
    
    # Class balance test via target
    assert "gender" in res.class_balance
    assert res.class_balance["gender"].class_counts["M"] == 3
