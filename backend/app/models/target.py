import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import TargetStatus, TargetRunStatus, JobStatus


class Target(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "targets"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    niche: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sub_niche: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    geography: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    
    status: Mapped[TargetStatus] = mapped_column(
        SQLEnum(TargetStatus, name="target_status_enum"), default=TargetStatus.ACTIVE, nullable=False
    )

    filters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    opportunity_types: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    source_configuration: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    target_runs: Mapped[List["TargetRun"]] = relationship("TargetRun", back_populates="target", cascade="all, delete-orphan")


class TargetRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "target_runs"

    target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("targets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target: Mapped["Target"] = relationship("Target", back_populates="target_runs")

    status: Mapped[TargetRunStatus] = mapped_column(
        SQLEnum(TargetRunStatus, name="target_run_status_enum"), default=TargetRunStatus.QUEUED, nullable=False
    )

    total_discovered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_verified: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_qualified: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_human_review: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_outreach_ready: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_log: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="target_run", cascade="all, delete-orphan")


class Job(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "jobs"

    target_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("target_runs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    target_run: Mapped[Optional["TargetRun"]] = relationship("TargetRun", back_populates="jobs")

    type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, name="job_status_enum"), default=JobStatus.PENDING, nullable=False, index=True
    )

    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    error_log: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
