import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import (
    VerificationCheckType,
    VerificationResultStatus,
    EvidenceType,
    ReviewActionType,
)


class VerificationResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "verification_results"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="verification_results")

    check_type: Mapped[VerificationCheckType] = mapped_column(
        SQLEnum(VerificationCheckType, name="verification_check_type_enum"), nullable=False, index=True
    )
    result: Mapped[VerificationResultStatus] = mapped_column(
        SQLEnum(VerificationResultStatus, name="verification_result_status_enum"), nullable=False, index=True
    )
    evidence: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    evidences: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="verification_result")


class Evidence(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "evidence"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="evidence")

    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_url_or_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    evidence_type: Mapped[EvidenceType] = mapped_column(
        SQLEnum(EvidenceType, name="evidence_type_enum"), default=EvidenceType.OBSERVED_FACT, nullable=False, index=True
    )
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    verification_result_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("verification_results.id", ondelete="SET NULL"), nullable=True
    )
    verification_result: Mapped[Optional["VerificationResult"]] = relationship("VerificationResult", back_populates="evidences")


class ReviewAction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "review_actions"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="review_actions")

    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    before_value: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    after_value: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    action_type: Mapped[ReviewActionType] = mapped_column(
        SQLEnum(ReviewActionType, name="review_action_type_enum"), nullable=False, index=True
    )
    reason: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
