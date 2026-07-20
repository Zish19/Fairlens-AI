from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from typing import Optional
from apps.api.core.jobs import JobStatus

class UploadJobBase(BaseModel):
    status: JobStatus
    progress: int = 0
    error_message: Optional[str] = None

class UploadJobResponse(UploadJobBase):
    id: uuid.UUID
    dataset_version_id: uuid.UUID
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
