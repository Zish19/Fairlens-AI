from abc import ABC, abstractmethod
from typing import Callable, Any, Optional
from fastapi import BackgroundTasks
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RECEIVED = "RECEIVED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"
    NOT_FOUND = "NOT_FOUND"

VALID_TRANSITIONS = {
    JobStatus.QUEUED: {JobStatus.RECEIVED, JobStatus.CANCELLED},
    JobStatus.RECEIVED: {JobStatus.RUNNING, JobStatus.FAILED},
    JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.RETRYING},
    JobStatus.RETRYING: {JobStatus.RECEIVED, JobStatus.FAILED},
    JobStatus.COMPLETED: set(),  # terminal
    JobStatus.FAILED: set(),     # terminal
    JobStatus.CANCELLED: set(),  # terminal
}

def is_valid_transition(current: JobStatus, target: JobStatus) -> bool:
    if current == target:
        return True
    if current not in VALID_TRANSITIONS:
        return False
    return target in VALID_TRANSITIONS[current]

class JobQueue(ABC):
    """Abstract interface for background job queues."""
    
    @abstractmethod
    def enqueue(self, job_id: str, func: Callable, *args, **kwargs) -> str:
        """Enqueues a task and returns the job ID."""
        pass
        
    @abstractmethod
    def status(self, job_id: str) -> JobStatus:
        """Returns the current status of the job."""
        pass
        
    @abstractmethod
    def cancel(self, job_id: str) -> bool:
        """Attempts to cancel the job."""
        pass


class FastAPIBackgroundQueue(JobQueue):
    """
    Lightweight queue using FastAPI BackgroundTasks.
    State is ephemeral and stored in memory.
    """
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks
        # In a real system, status would be read from Redis/DB
        # Here we just rely on the fact it's passed to FastAPI
        
    def enqueue(self, job_id: str, func: Callable, *args, **kwargs) -> str:
        self.background_tasks.add_task(func, *args, **kwargs)
        return job_id
        
    def status(self, job_id: str) -> JobStatus:
        # FastAPI BackgroundTasks doesn't expose introspection
        # We rely on the DB (UploadJob) to track status in our app
        return JobStatus.QUEUED 
        
    def cancel(self, job_id: str) -> bool:
        raise NotImplementedError("Cancellation is not supported for FastAPI BackgroundTasks.")

class CeleryJobQueue(JobQueue):
    """
    Queue abstraction wrapping Celery, preventing Celery imports in routers.
    """
    def __init__(self, celery_app):
        self.celery_app = celery_app
        
    def enqueue(self, job_id: str, func: Callable, *args, **kwargs) -> str:
        # Assuming func is a celery @task registered in the celery_app
        from asgi_correlation_id import correlation_id
        req_id = correlation_id.get()
        headers = {}
        if req_id:
            headers["x-correlation-id"] = req_id
            
        task = func.apply_async(args=args, kwargs=kwargs, task_id=job_id, headers=headers)
        return task.id
        
    def status(self, job_id: str) -> JobStatus:
        from celery.result import AsyncResult
        res = AsyncResult(job_id, app=self.celery_app)
        state_mapping = {
            "PENDING": JobStatus.QUEUED,
            "RECEIVED": JobStatus.RECEIVED,
            "STARTED": JobStatus.RUNNING,
            "SUCCESS": JobStatus.COMPLETED,
            "FAILURE": JobStatus.FAILED,
            "RETRY": JobStatus.RETRYING,
            "REVOKED": JobStatus.CANCELLED
        }
        return state_mapping.get(res.state, JobStatus.FAILED)
        
    def cancel(self, job_id: str) -> bool:
        from celery.result import AsyncResult
        res = AsyncResult(job_id, app=self.celery_app)
        res.revoke(terminate=True)
        return True

def get_job_queue() -> JobQueue:
    """Dependency provider for JobQueue abstraction."""
    from apps.api.core.celery_app import celery_app
    return CeleryJobQueue(celery_app)
