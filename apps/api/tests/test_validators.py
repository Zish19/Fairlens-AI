import io
import pytest
import pandas as pd
from apps.api.services.validators import (
    ExtensionValidator,
    MimeValidator,
    SizeValidator,
    EncodingValidator,
    SchemaValidator,
    ValidationPipeline
)

def test_extension_validator():
    val = ExtensionValidator([".csv", ".json"])
    
    # Valid
    assert val.validate("data.csv", io.BytesIO(b"")).is_valid is True
    assert val.validate("data.JSON", io.BytesIO(b"")).is_valid is True
    
    # Invalid
    res = val.validate("data.txt", io.BytesIO(b""))
    assert res.is_valid is False
    assert res.error_code == "INVALID_EXTENSION"


def test_size_validator():
    val = SizeValidator(max_bytes=10)
    
    # Empty
    res = val.validate("data.csv", io.BytesIO(b""))
    assert res.is_valid is False
    assert res.error_code == "EMPTY_FILE"
    
    # Valid
    assert val.validate("data.csv", io.BytesIO(b"12345")).is_valid is True
    
    # Too large
    res = val.validate("data.csv", io.BytesIO(b"12345678901"))
    assert res.is_valid is False
    assert res.error_code == "FILE_TOO_LARGE"


def test_encoding_validator():
    val = EncodingValidator()
    
    # Valid UTF-8
    assert val.validate("data.csv", io.BytesIO("hello world".encode('utf-8'))).is_valid is True
    
    # Invalid UTF-16
    res = val.validate("data.csv", io.BytesIO("hello world".encode('utf-16')))
    assert res.is_valid is False
    assert res.error_code == "INVALID_ENCODING"
    
    # Skip excel
    assert val.validate("data.xlsx", io.BytesIO("hello world".encode('utf-16'))).is_valid is True


def test_schema_validator_duplicate_cols():
    val = SchemaValidator()
    csv_data = b"col1,col1\n1,2"
    res = val.validate("data.csv", io.BytesIO(csv_data))
    assert res.is_valid is False
    assert res.error_code == "DUPLICATE_COLUMNS"


def test_schema_validator_empty_dataset():
    val = SchemaValidator()
    csv_data = b"col1,col2\n"
    res = val.validate("data.csv", io.BytesIO(csv_data))
    assert res.is_valid is False
    assert res.error_code == "EMPTY_DATASET"


def test_schema_validator_nan_columns():
    val = SchemaValidator()
    csv_data = b"col1,col2\n1,\n2,\n"
    res = val.validate("data.csv", io.BytesIO(csv_data))
    assert res.is_valid is False
    assert res.error_code == "NAN_ONLY_COLUMNS"


def test_schema_validator_corrupted_csv():
    val = SchemaValidator()
    # Provide a binary chunk posing as CSV
    res = val.validate("data.csv", io.BytesIO(b"\x00\x01\x02"))
    assert res.is_valid is False
    assert res.error_code in ["MALFORMED_DATASET", "EMPTY_DATASET"]


def test_validation_pipeline():
    validators = [
        ExtensionValidator([".csv"]),
        SizeValidator(max_bytes=100)
    ]
    pipeline = ValidationPipeline(validators)
    
    # Fails first validator
    res1 = pipeline.execute("data.txt", io.BytesIO(b"abc"))
    assert res1.is_valid is False
    assert res1.error_code == "INVALID_EXTENSION"
    
    # Fails second validator
    res2 = pipeline.execute("data.csv", io.BytesIO(b"x" * 105))
    assert res2.is_valid is False
    assert res2.error_code == "FILE_TOO_LARGE"
    
    # Passes both
    res3 = pipeline.execute("data.csv", io.BytesIO(b"valid content"))
    assert res3.is_valid is True
