import os
import uuid
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from apps.api.core.db import engine, SessionLocal
from apps.api.models.base import Base
from apps.api.models import User, Dataset, DatasetVersion, Analysis, RefreshToken, MetricResult, UploadJob

from apps.api.core.security import get_current_user

mock_user = User(id=uuid.uuid4(), email="test@example.com")

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.add(User(id=mock_user.id, email=mock_user.email, hashed_password="pwd"))
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def setup_auth():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    from apps.api.core.jobs import get_job_queue
    from apps.api.tests.mock_queue import MockJobQueue
    app.dependency_overrides[get_job_queue] = MockJobQueue
    
    yield
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    if get_job_queue in app.dependency_overrides:
        del app.dependency_overrides[get_job_queue]

client = TestClient(app)



def test_upload_success():
    # Use a small valid CSV for the test
    file_content = b"header1,header2\nvalue1,value2"
    
    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test.csv", file_content, "text/csv")}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "datasetId" in data["data"]
    assert "jobId" in data["data"]
    assert data["data"]["status"] == "QUEUED"
    assert data["data"]["size"] == len(file_content)

def test_upload_invalid_extension():
    file_content = b"some random text"
    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test.txt", file_content, "text/plain")}
    )
    
    assert response.status_code == 400
    assert "INVALID_EXTENSION" in response.json()["detail"]
