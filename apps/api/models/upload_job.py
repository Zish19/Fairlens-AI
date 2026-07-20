import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.models.base import Base, UUIDMixin, TimestampMixin

from apps.api.core.jobs import JobStatus

class UploadJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "upload_jobs"

    dataset_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dataset_versions.id"), index=True, nullable=False)
    
    status: Mapped[str] = mapped_column(String, default=JobStatus.QUEUED, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    dataset_version: Mapped["DatasetVersion"] = relationship("DatasetVersion", back_populates="upload_jobs")
