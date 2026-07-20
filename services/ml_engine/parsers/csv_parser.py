import pandas as pd
from typing import Optional

def parse(path: str) -> pd.DataFrame:
    """
    Parses a CSV file into a pandas DataFrame.
    """
    # Uses python engine as fallback if C engine fails on weird delimiters/newlines
    try:
        return pd.read_csv(path, engine='c')
    except Exception:
        return pd.read_csv(path, engine='python')
