import pandas as pd

def parse(path: str) -> pd.DataFrame:
    """
    Parses a JSON file into a pandas DataFrame.
    Tries different orientations safely.
    """
    try:
        return pd.read_json(path, orient='records')
    except ValueError:
        # Fallback to column orientation if records fails
        return pd.read_json(path, orient='columns')
