import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import uuid

from apps.api.main import app
from apps.api.core.db import get_db
from apps.api.models import User, Dataset, DatasetVersion, Analysis, RefreshToken, MetricResult, UploadJob
from apps.api.models.base import Base
from apps.api.schemas.analysis import AnalysisConfig, TrainingConfig, FairnessConfig
from apps.api.core.security import get_current_user

from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if get_db in app.dependency_overrides:
        del app.dependency_overrides[get_db]

mock_user = User(id=uuid.uuid4(), email="test@example.com")

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

@pytest.fixture
def test_db_session(tmp_path):
    db = TestingSessionLocal()
    
    # Create mock dataset & version
    dataset = Dataset(name="Test Analysis Dataset", owner_id=mock_user.id)
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    
    # Create real dummy CSV for background job to read
    csv_file = tmp_path / "dummy.csv"
    df = pd.DataFrame({
        "income": [1, 0, 1, 0],
        "gender": ["M", "F", "M", "F"],
        "feature": [1, 2, 3, 4]
    })
    df.to_csv(csv_file, index=False)
    
    version = DatasetVersion(
        dataset_id=dataset.id,
        owner_id=dataset.owner_id,
        storage_path=str(csv_file),
        sha256="dummyhash",
        mime_type="text/csv",
        file_size=1024
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    
    yield db, version
    db.close()


def test_analysis_submission(test_db_session):
    db, version = test_db_session
    client = TestClient(app)

    payload = {
        "config": {
            "schema_version": 1,
            "training": {
                "algorithm": "RandomForestClassifier",
                "test_size": 0.2
            },
            "fairness": {
                "target_column": "income",
                "sensitive_attribute": "gender",
                "positive_label": ">50K",
                "metrics": ["DemographicParity", "EqualOpportunity"]
            }
        }
    }
    
    response = client.post(f"/api/v1/datasets/{version.id}/analyze", json=payload)
    
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["status"] == "QUEUED"
    assert data["dataset_version_id"] == str(version.id)
    assert data["config"]["fairness"]["target_column"] == "income"
    
    # Test GET endpoint
    analysis_id = data["id"]
    get_response = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == analysis_id
    assert get_data["status"] == "QUEUED"

def test_fairness_service_logic():
    # Unit test for FairnessService directly
    from services.ml_engine.fairness.service import FairnessService
    
    config = AnalysisConfig(
        training=TrainingConfig(test_size=0.5, random_state=42),
        fairness=FairnessConfig(
            target_column="income",
            sensitive_attribute="gender",
            positive_label=1,
            metrics=["DemographicParity"]
        )
    )
    
    # Dummy data: 10 rows
    # Males tend to get 1, females 0 (synthetic bias)
    df = pd.DataFrame({
        "income": [1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
        "gender": ["M", "M", "M", "M", "M", "F", "F", "F", "F", "F"],
        "feature1": [5, 4, 5, 2, 4, 1, 1, 2, 1, 5]
    })
    
    service = FairnessService(config)
    summary, model, X_test = service.analyze(df)
    
    assert len(summary.warnings) == 0
    assert len(summary.metrics) > 0
    
    # Should have DemographicParityDifference and SelectionRates
    metric_names = [m.metric_name for m in summary.metrics]
    assert "DemographicParityDifference" in metric_names
    assert "SelectionRate" in metric_names
