from sqlalchemy import String, Integer, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import uuid

from apps.api.models.base import Base, UUIDMixin, TimestampMixin

class Dataset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Optimistic concurrency locking version
    version_lock: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    __mapper_args__ = {
        "version_id_col": version_lock
    }

    # Relationships
    versions: Mapped[List["DatasetVersion"]] = relationship(
        "DatasetVersion", back_populates="dataset", cascade="all, delete-orphan"
    )
