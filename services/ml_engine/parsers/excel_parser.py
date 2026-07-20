import pandas as pd

def parse(path: str) -> pd.DataFrame:
    """
    Parses an Excel file into a pandas DataFrame.
    Reads the first sheet by default.
    """
    return pd.read_excel(path, engine="openpyxl")
