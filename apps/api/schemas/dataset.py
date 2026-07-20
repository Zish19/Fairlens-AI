from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from typing import Optional, List

class DatasetVersionBase(BaseModel):
    storage_path: str
    sha256: str
    mime_type: str
    file_size: int
    schema_hash: Optional[str] = None

class DatasetVersionResponse(DatasetVersionBase):
    id: uuid.UUID
    dataset_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DatasetBase(BaseModel):
    name: str
    owner_id: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    pass

class DatasetResponse(DatasetBase):
    id: uuid.UUID
    version_lock: int
    created_at: datetime
    updated_at: datetime
    versions: List[DatasetVersionResponse] = []

    model_config = ConfigDict(from_attributes=True)
