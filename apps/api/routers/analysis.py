from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import uuid
import pandas as pd
import os

from apps.api.core.db import get_db
from apps.api.models.dataset_version import DatasetVersion
from apps.api.models.analysis import Analysis, MetricResult
from apps.api.schemas.analysis import AnalysisConfigRequest, AnalysisResponse, MetricResultResponse
from apps.api.core.jobs import JobStatus, JobQueue, get_job_queue
from apps.api.core.security import get_current_user
from apps.api.models.user import User
from apps.api.core.cache import CacheService

router = APIRouter(tags=["analysis"])

from apps.api.tasks.analysis_tasks import run_analysis_task

@router.post("/datasets/{dataset_version_id}/analyze", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_analysis(
    dataset_version_id: uuid.UUID,
    request: AnalysisConfigRequest,
    queue: JobQueue = Depends(get_job_queue),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    version = db.query(DatasetVersion).filter(DatasetVersion.id == dataset_version_id, DatasetVersion.owner_id == current_user.id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Dataset version not found.")
        
    # Create Analysis entity
    analysis = Analysis(
        dataset_version_id=dataset_version_id,
        owner_id=current_user.id,
        status=JobStatus.QUEUED,
        config=request.config.model_dump()
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Enqueue background job
    queue.enqueue(str(analysis.id), run_analysis_task, str(analysis.id), str(version.id))
    
    return analysis

@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cache_key = f"analysis:{analysis_id}"
    cached = await CacheService.get(cache_key)
    if cached:
        return cached

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.owner_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
        
    response_data = AnalysisResponse.model_validate(analysis).model_dump(mode='json')
    if analysis.status == JobStatus.COMPLETED:
        await CacheService.set(cache_key, response_data)
        
    return response_data

from typing import List
from apps.api.models.dataset import Dataset
from apps.api.schemas.analysis import DatasetAnalysesResponse, DatasetVersionAnalyses

@router.get("/analyses", response_model=List[AnalysisResponse])
def list_analyses(skip: int = 0, limit: int = 50, status: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Analysis).filter(Analysis.owner_id == current_user.id)
    if status:
        query = query.filter(Analysis.status == status)
    query = query.order_by(Analysis.created_at.desc())
    return query.offset(skip).limit(limit).all()

@router.get("/datasets/{dataset_id}/analyses", response_model=DatasetAnalysesResponse)
def list_dataset_analyses(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
        
    versions = []
    for version in sorted(dataset.versions, key=lambda v: v.created_at, reverse=True):
        analyses = db.query(Analysis).filter(Analysis.dataset_version_id == version.id).order_by(Analysis.created_at.desc()).all()
        versions.append(DatasetVersionAnalyses(
            version_id=version.id,
            storage_path=version.storage_path,
            created_at=version.created_at,
            analyses=analyses
        ))
        
    return DatasetAnalysesResponse(dataset_id=dataset_id, versions=versions)

@router.get("/analyses/{analysis_id}/explainability")
async def get_analysis_explainability(analysis_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cache_key = f"explainability:{analysis_id}"
    cached = await CacheService.get(cache_key)
    if cached:
        return cached

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.owner_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
        
    response_data = {"feature_importance": analysis.feature_importance}
    if analysis.status == JobStatus.COMPLETED:
        await CacheService.set(cache_key, response_data)
        
    return response_data

from services.ml_engine.insights.builder import InsightBuilder
from services.ml_engine.insights.ai_service import get_ai_service
from services.ml_engine.insights.schemas import InsightResponse

@router.get("/analyses/{analysis_id}/insights", response_model=InsightResponse)
async def get_analysis_insights(analysis_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cache_key = f"insights:{analysis_id}"
    cached = await CacheService.get(cache_key)
    if cached:
        return cached

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.owner_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    
    if analysis.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis must be COMPLETED to generate insights.")
        
    context = InsightBuilder.build_context(analysis)
    ai_service = get_ai_service()
    insights = ai_service.generate_insights(context)
    
    response_data = insights.model_dump(mode='json')
    await CacheService.set(cache_key, response_data)
    
    return response_data
