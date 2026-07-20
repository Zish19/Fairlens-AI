from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime
from typing import Optional

from apps.api.schemas.job import JobStatus

class UploadResponseData(BaseModel):
    dataset_id: uuid.UUID = Field(..., alias="datasetId")
    dataset_version_id: uuid.UUID = Field(..., alias="datasetVersionId")
    job_id: uuid.UUID = Field(..., alias="jobId")
    status: JobStatus
    uploaded_at: datetime = Field(..., alias="uploadedAt")
    filename: str
    size: int
    
    model_config = ConfigDict(populate_by_name=True)

class UploadResponse(BaseModel):
    success: bool
    data: UploadResponseData
    meta: Optional[dict] = {}
