from apps.api.core.jobs import JobQueue, JobStatus
from typing import Callable
import uuid

class MockJobQueue(JobQueue):
    def enqueue(self, job_id: str, func: Callable, *args, **kwargs) -> str:
        # Instead of calling apply_async, we can just return the job_id
        # We assume the background task won't actually be awaited in these test cases
        # because the original FastAPIBackgroundQueue also didn't block the request.
        # But if we want to run it synchronously for tests:
        try:
            # We skip running for unit tests of endpoints to keep them fast
            # and to avoid side effects. 
            pass
        except Exception:
            pass
        return job_id
        
    def status(self, job_id: str) -> JobStatus:
        return JobStatus.QUEUED
        
    def cancel(self, job_id: str) -> bool:
        return True
