import uuid
from sqlalchemy import String, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from apps.api.models.base import Base, UUIDMixin, TimestampMixin

json_type = JSON().with_variant(JSONB, "postgresql")

from apps.api.core.jobs import JobStatus

class Analysis(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analyses"

    dataset_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dataset_versions.id"), index=True, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default=JobStatus.QUEUED)
    config: Mapped[dict] = mapped_column(json_type, nullable=False)
    recommendations: Mapped[list] = mapped_column(json_type, nullable=True, default=list)
    feature_importance: Mapped[list] = mapped_column(json_type, nullable=True, default=list)
    
    # Relationships
    dataset_version = relationship("DatasetVersion")
    metrics: Mapped[List["MetricResult"]] = relationship(
        "MetricResult", back_populates="analysis", cascade="all, delete-orphan"
    )

class MetricResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "metric_results"

    analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analyses.id"), index=True, nullable=False)
    
    metric_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    subgroup: Mapped[str | None] = mapped_column(String, nullable=True)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    interpretation: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="metrics")
