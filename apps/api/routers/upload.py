import io
import uuid
import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, status, Request
from sqlalchemy.orm import Session

from apps.api.core.db import get_db
from apps.api.core.storage import get_storage_provider
from apps.api.core.jobs import JobQueue, get_job_queue
from apps.api.services.validators import get_default_validation_pipeline

from apps.api.models.dataset import Dataset
from apps.api.models.dataset_version import DatasetVersion
from apps.api.models.upload_job import UploadJob
from apps.api.core.jobs import JobStatus
from apps.api.models.user import User

from apps.api.schemas.upload import UploadResponse, UploadResponseData
from apps.api.core.config import settings
from apps.api.core.security import get_current_user

router = APIRouter()

from apps.api.tasks.upload_tasks import process_upload_task

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    request: Request,
    queue: JobQueue = Depends(get_job_queue),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    storage = get_storage_provider("local")
    validator = get_default_validation_pipeline()
    
    file_bytes = await file.read()
    file_stream = io.BytesIO(file_bytes)
    
    filename = file.filename or "unknown.csv"
    val_result = validator.execute(filename, file_stream)
    if not val_result.is_valid:
        raise HTTPException(
            status_code=400, 
            detail=f"Validation failed: {val_result.error_code} - {val_result.message}"
        )
        
    file_stream.seek(0)
    file_size = len(file_bytes)
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    
    dataset_id = uuid.uuid4()
    dataset = Dataset(
        id=dataset_id,
        name=filename,
        owner_id=current_user.id
    )
    db.add(dataset)
    
    dataset_version_id = uuid.uuid4()
    rel_path, abs_path = storage.generate_path(filename)
    
    file_stream.seek(0)
    saved_path = storage.save(file_stream, rel_path)
    
    version = DatasetVersion(
        id=dataset_version_id,
        dataset_id=dataset_id,
        owner_id=current_user.id,
        storage_path=saved_path,
        sha256=sha256,
        mime_type=file.content_type or "application/octet-stream",
        file_size=file_size
    )
    db.add(version)
    
    job_id = uuid.uuid4()
    from datetime import timezone
    job = UploadJob(
        id=job_id,
        dataset_version_id=dataset_version_id,
        status=JobStatus.QUEUED,
        started_at=datetime.now(timezone.utc)
    )
    db.add(job)
    
    db.commit()
    db.refresh(dataset)
    db.refresh(version)
    db.refresh(job)
    
    queue.enqueue(
        str(job_id), 
        process_upload_task, 
        str(job_id),
        str(dataset_version_id), 
        saved_path
    )
    
    return UploadResponse(
        success=True,
        data=UploadResponseData(
            datasetId=dataset.id,
            datasetVersionId=version.id,
            jobId=job.id,
            status=job.status,
            uploadedAt=version.created_at,
            filename=filename,
            size=file_size
        )
    )

@router.get("", response_model=dict)
def list_datasets(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).order_by(Dataset.created_at.desc()).all()
    return {
        "datasets": [
            {
                "id": str(d.id),
                "name": d.name,
                "owner_id": str(d.owner_id),
                "created_at": d.created_at.isoformat(),
                "versions": [
                    {
                        "id": str(v.id),
                        "mime_type": v.mime_type,
                        "created_at": v.created_at.isoformat()
                    } for v in d.versions
                ]
            } for d in datasets
        ]
    }
