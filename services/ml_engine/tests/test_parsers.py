import os
import pytest
import pandas as pd

from services.ml_engine.parsers import csv_parser, excel_parser, json_parser

def test_csv_parser(tmp_path):
    file_path = tmp_path / "test.csv"
    file_path.write_text("a,b\n1,2\n3,4")
    
    df = csv_parser.parse(str(file_path))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["a", "b"]
    assert df.iloc[0]["a"] == 1


def test_excel_parser(tmp_path):
    file_path = tmp_path / "test.xlsx"
    df_orig = pd.DataFrame({"a": [1, 3], "b": [2, 4]})
    df_orig.to_excel(file_path, index=False)
    
    df = excel_parser.parse(str(file_path))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["a", "b"]
    assert df.iloc[0]["a"] == 1


def test_json_parser_records(tmp_path):
    file_path = tmp_path / "test_records.json"
    file_path.write_text('[{"a": 1, "b": 2}, {"a": 3, "b": 4}]')
    
    df = json_parser.parse(str(file_path))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["a", "b"]


def test_json_parser_columns(tmp_path):
    file_path = tmp_path / "test_columns.json"
    file_path.write_text('{"a": {"0": 1, "1": 3}, "b": {"0": 2, "1": 4}}')
    
    df = json_parser.parse(str(file_path))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["a", "b"]
