import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from apps.api.models.base import Base
from apps.api.models import User, Dataset, DatasetVersion, Analysis, RefreshToken, MetricResult, UploadJob
from apps.api.core.db import engine, get_db
from sqlalchemy.orm import sessionmaker

# Setup test DB (ideally this points to a separate test DB like Postgres in CI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    from apps.api.core.jobs import get_job_queue
    from apps.api.tests.mock_queue import MockJobQueue
    app.dependency_overrides[get_job_queue] = MockJobQueue
    
    yield
    Base.metadata.drop_all(bind=engine)
    if get_db in app.dependency_overrides:
        del app.dependency_overrides[get_db]
    if get_job_queue in app.dependency_overrides:
        del app.dependency_overrides[get_job_queue]

def test_integration_flow(setup_db):
    # 1. Register User A
    resp_reg_a = client.post("/api/v1/auth/register", json={
        "email": "userA@example.com",
        "password": "Password123!"
    })
    assert resp_reg_a.status_code == 200
    
    # 2. Login User A
    resp_login_a = client.post("/api/v1/auth/login", data={
        "username": "userA@example.com",
        "password": "Password123!"
    })
    assert resp_login_a.status_code == 200
    tokens_a = resp_login_a.json()
    token_a = tokens_a["access_token"]
    
    # 3. Register & Login User B
    client.post("/api/v1/auth/register", json={
        "email": "userB@example.com",
        "password": "Password123!"
    })
    resp_login_b = client.post("/api/v1/auth/login", data={
        "username": "userB@example.com",
        "password": "Password123!"
    })
    tokens_b = resp_login_b.json()
    token_b = tokens_b["access_token"]
    
    # 4. Upload Dataset by User A
    # Create dummy csv content
    file_content = b"col1,col2\n1,2\n3,4"
    resp_upload = client.post(
        "/api/v1/datasets/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"file": ("test.csv", file_content, "text/csv")}
    )
    assert resp_upload.status_code == 201
    upload_data = resp_upload.json()["data"]
    dataset_id = upload_data["datasetId"]
    
    # 5. List Datasets for User A (Should see the dataset)
    resp_list_a = client.get(
        "/api/v1/datasets",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp_list_a.status_code == 200
    assert len(resp_list_a.json()["datasets"]) == 1
    
    # 6. List Datasets for User B (Should NOT see the dataset)
    resp_list_b = client.get(
        "/api/v1/datasets",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp_list_b.status_code == 200
    
    datasets_a = resp_list_a.json()["datasets"]
    datasets_b = resp_list_b.json()["datasets"]
    print(f"Token A datasets: {datasets_a}")
    print(f"Token B datasets: {datasets_b}")
    print(f"Token A: {token_a}")
    print(f"Token B: {token_b}")
    
    assert len(datasets_b) == 0
