import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from apps.api.models.base import Base, UUIDMixin, TimestampMixin

class DatasetVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "dataset_versions"

    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id"), index=True, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False, index=True)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="versions")
    upload_jobs: Mapped[List["UploadJob"]] = relationship(
        "UploadJob", back_populates="dataset_version", cascade="all, delete-orphan"
    )
