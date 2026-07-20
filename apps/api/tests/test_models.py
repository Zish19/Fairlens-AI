import uuid
from datetime import datetime
from apps.api.models.dataset import Dataset
from apps.api.models.dataset_version import DatasetVersion
from apps.api.models.upload_job import UploadJob
from apps.api.core.jobs import JobStatus
from apps.api.schemas.dataset import DatasetCreate, DatasetResponse, DatasetVersionResponse
from apps.api.schemas.upload import UploadResponse, UploadResponseData

def test_models_importable():
    # Test ORM instantiation
    d_id = uuid.uuid4()
    d = Dataset(id=d_id, name="Test", owner_id="user1")
    dv = DatasetVersion(dataset_id=d_id, storage_path="file.csv", sha256="abc", mime_type="text/csv", file_size=123)
    j = UploadJob(dataset_version_id=uuid.uuid4(), status=JobStatus.QUEUED)
    
    assert d.name == "Test"
    assert j.status == JobStatus.QUEUED

def test_schemas_instantiation():
    # Test Pydantic schemas
    create_dto = DatasetCreate(name="Test", owner_id="user1")
    assert create_dto.name == "Test"
    
    upload_resp = UploadResponseData(
        datasetId=uuid.uuid4(),
        datasetVersionId=uuid.uuid4(),
        jobId=uuid.uuid4(),
        status=JobStatus.QUEUED,
        uploadedAt=datetime.now(),
        filename="test.csv",
        size=100
    )
    assert upload_resp.size == 100
