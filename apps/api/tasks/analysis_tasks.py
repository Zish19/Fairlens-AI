import uuid
import pandas as pd
from typing import Optional

from apps.api.core.celery_app import celery_app
from apps.api.core.db import SessionLocal
from apps.api.models.analysis import Analysis, MetricResult
from apps.api.models.dataset_version import DatasetVersion
from apps.api.core.jobs import JobStatus
from services.ml_engine.fairness.service import FairnessService
from services.ml_engine.explainability.explainer import ExplainerService
from apps.api.schemas.analysis import AnalysisConfig

@celery_app.task(bind=True, max_retries=3)
def run_analysis_task(self, analysis_id_str: str, dataset_version_id_str: str):
    analysis_id = uuid.UUID(analysis_id_str)
    dataset_version_id = uuid.UUID(dataset_version_id_str)
    
    db = SessionLocal()
    try:
        # Re-fetch entities
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        version = db.query(DatasetVersion).filter(DatasetVersion.id == dataset_version_id).first()
        
        if not analysis or not version:
            raise ValueError(f"Analysis or DatasetVersion not found.")
            
        analysis.status = JobStatus.RUNNING
        db.commit()
        
        storage_path = version.storage_path
        
        # Load dataset
        if storage_path.endswith('.csv'):
            df = pd.read_csv(storage_path)
        elif storage_path.endswith('.xlsx'):
            df = pd.read_excel(storage_path)
        elif storage_path.endswith('.json'):
            df = pd.read_json(storage_path)
        else:
            raise ValueError("Unsupported file format for analysis.")
            
        # Parse config back to pydantic
        config_obj = AnalysisConfig.model_validate(analysis.config)
        
        # 1. Train model & Compute Fairness
        service = FairnessService(config_obj)
        summary, model, X_test = service.analyze(df)
        
        # 2. Compute Explainability (SHAP)
        if model is not None and X_test is not None:
            explainer_summary = ExplainerService.explain_model(model, X_test)
            analysis.feature_importance = [fi.model_dump() for fi in explainer_summary.global_explanation.feature_importance]
        else:
            analysis.feature_importance = []
            
        # 3. Persist metric results
        for m in summary.metrics:
            metric_res = MetricResult(
                analysis_id=analysis.id,
                metric_name=m.metric_name,
                metric_value=m.metric_value,
                subgroup=m.subgroup,
                threshold=m.threshold,
                interpretation=m.interpretation
            )
            db.add(metric_res)
            
        analysis.status = JobStatus.COMPLETED
        analysis.recommendations = summary.recommendations
        
        db.commit()
    except ValueError as e:
        # Deterministic errors should fail immediately, no retry
        print(f"Analysis {analysis_id} failed deterministically: {e}")
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = JobStatus.FAILED
            db.commit()
    except Exception as exc:
        print(f"Analysis {analysis_id} failed with transient error: {exc}")
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = JobStatus.RETRYING
            db.commit()
        raise self.retry(exc=exc, countdown=10) # Retry after 10s
    finally:
        db.close()
