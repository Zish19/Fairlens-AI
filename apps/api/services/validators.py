import os
from abc import ABC, abstractmethod
from typing import BinaryIO, List, Optional
from pydantic import BaseModel
import chardet
import pandas as pd

class ValidationResult(BaseModel):
    is_valid: bool
    error_code: Optional[str] = None
    message: Optional[str] = None


class DatasetValidator(ABC):
    """Abstract base class for dataset validators in the pipeline."""
    
    @abstractmethod
    def validate(self, file_path: str, file_obj: BinaryIO) -> ValidationResult:
        """
        Validates the dataset. 
        Note: file_obj read position should be reset if it's read by the validator.
        """
        pass


class ValidationPipeline:
    """Runs a sequence of validators, stopping at the first failure."""
    def __init__(self, validators: List[DatasetValidator]):
        self.validators = validators

    def execute(self, file_path: str, file_obj: BinaryIO) -> ValidationResult:
        for validator in self.validators:
            # Always reset file pointer before each validator
            file_obj.seek(0)
            result = validator.validate(file_path, file_obj)
            if not result.is_valid:
                return result
        return ValidationResult(is_valid=True)


class ExtensionValidator(DatasetValidator):
    def __init__(self, allowed_extensions: List[str]):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]

    def validate(self, file_path: str, file_obj: BinaryIO) -> ValidationResult:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.allowed_extensions:
            return ValidationResult(
                is_valid=False, 
                error_code="INVALID_EXTENSION", 
                message=f"Extension '{ext}' is not supported. Allowed: {self.allowed_extensions}"
            )
        return ValidationResult(is_valid=True)


class MimeValidator(DatasetValidator):
    def __init__(self, allowed_mimes: List[str]):
        self.allowed_mimes = allowed_mimes

    def validate(self, file_path: str, file_obj: BinaryIO) -> ValidationResult:
        # In a real scenario we'd use python-magic, but we'll use a naive check 
        # or rely on FastAPI's provided content-type via the upload route for MIME.
        # Since we only have the file_obj here, we'll simulate magic checking for CSV/JSON/Excel.
        file_obj.seek(0)
        header = file_obj.read(4)
        
        # Very naive magic bytes check for zip/excel (PK\x03\x04)
        is_zip = header.startswith(b"PK\x03\x04")
        
        # If it's a known extension, we just trust the extension for now, 
        # or we check if it is text-like.
        ext = os.path.splitext(file_path)[1].lower()
        
        mime = "application/octet-stream"
        if ext == ".csv":
            mime = "text/csv"
        elif ext == ".json":
            mime = "application/json"
        elif ext in [".xls", ".xlsx"] and is_zip:
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        if mime not in self.allowed_mimes:
            return ValidationResult(
                is_valid=False,
                error_code="INVALID_MIME_TYPE",
                message=f"MIME type '{mime}' is not allowed."
            )
        return ValidationResult(is_valid=True)


class SizeValidator(DatasetValidator):
    def __init__(self, max_bytes: int):
        self.max_bytes = max_bytes

    def validate(self, file_path: str, file_obj: BinaryIO) -> ValidationResult:
        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
        
        if size == 0:
            return ValidationResult(
                is_valid=False,
                error_code="EMPTY_FILE",
                message="The dataset file is empty."
            )
            
        if size > self.max_bytes:
            return ValidationResult(
                is_valid=False,
                error_code="FILE_TOO_LARGE",
                message=f"File exceeds maximum allowed size of {self.max_bytes} bytes."
            )
            
        return ValidationResult(is_valid=True)


class EncodingValidator(DatasetValidator):
    def validate(self, file_path: str, file_obj: BinaryIO) -> ValidationResult:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".xls", ".xlsx"]:
            return ValidationResult(is_valid=True) # Excel is binary, encoding check not applicable
            
        file_obj.seek(0)
        raw_data = file_obj.read(10000) # Check first 10KB
        
        if not raw_data:
            return ValidationResult(is_valid=True)
            
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        
        # We enforce UTF-8 or ASCII for text datasets
        if encoding is not None and encoding.lower() not in ['utf-8', 'ascii']:
            return ValidationResult(
                is_valid=False,
                error_code="INVALID_ENCODING",
                message=f"Unsupported encoding '{encoding}'. Only UTF-8 or ASCII is supported."
            )
        return ValidationResult(is_valid=True)


class SchemaValidator(DatasetValidator):
    def __init__(self, max_rows: int = 1000000, max_cols: int = 1000):
        self.max_rows = max_rows
        self.max_cols = max_cols

    def validate(self, file_path: str, file_obj: BinaryIO) -> ValidationResult:
        ext = os.path.splitext(file_path)[1].lower()
        file_obj.seek(0)
        
        try:
            if ext == ".csv":
                df = pd.read_csv(file_obj, nrows=100) # Just read a chunk for schema validation
            elif ext in [".xls", ".xlsx"]:
                df = pd.read_excel(file_obj, nrows=100)
            elif ext == ".json":
                df = pd.read_json(file_obj) # json might be hard to chunk
            else:
                return ValidationResult(is_valid=True) # Cannot schema-validate unknown format
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_code="MALFORMED_DATASET",
                message=f"Failed to parse dataset for schema validation: {str(e)}"
            )

        if df.empty:
            return ValidationResult(
                is_valid=False,
                error_code="EMPTY_DATASET",
                message="Dataset has no records (only headers or completely empty)."
            )

        # Duplicate columns check
        # pandas read_csv mangles duplicate columns by adding .1, .2
        # we can detect this by checking if any column has a .1 suffix and the original exists
        import re
        for col in df.columns:
            match = re.search(r'^(.*)\.\d+$', str(col))
            if match and match.group(1) in df.columns:
                return ValidationResult(
                    is_valid=False,
                    error_code="DUPLICATE_COLUMNS",
                    message="Dataset contains duplicate column names."
                )
            
        # NaN-only columns
        nan_cols = df.columns[df.isna().all()].tolist()
        if nan_cols:
            return ValidationResult(
                is_valid=False,
                error_code="NAN_ONLY_COLUMNS",
                message=f"Dataset contains columns with entirely missing values: {nan_cols}"
            )
            
        # Max cols
        if len(df.columns) > self.max_cols:
            return ValidationResult(
                is_valid=False,
                error_code="TOO_MANY_COLUMNS",
                message=f"Dataset has {len(df.columns)} columns. Max allowed is {self.max_cols}."
            )
            
        # Unsupported dtypes (e.g. complex numbers)
        for col, dtype in df.dtypes.items():
            if dtype.name == 'complex128' or dtype.name == 'complex64':
                return ValidationResult(
                    is_valid=False,
                    error_code="UNSUPPORTED_DTYPE",
                    message=f"Column '{col}' has unsupported data type '{dtype.name}'."
                )

        return ValidationResult(is_valid=True)


def get_default_validation_pipeline() -> ValidationPipeline:
    return ValidationPipeline([
        ExtensionValidator([".csv", ".json", ".xlsx", ".xls"]),
        MimeValidator(["text/csv", "application/json", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]),
        SizeValidator(max_bytes=100 * 1024 * 1024), # 100 MB
        EncodingValidator(),
        SchemaValidator(max_rows=1000000, max_cols=500)
    ])
