import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import LifecycleStatus


class Business(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Address Details
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    lifecycle_status: Mapped[LifecycleStatus] = mapped_column(
        SQLEnum(LifecycleStatus, name="lifecycle_status_enum"), default=LifecycleStatus.DISCOVERED, nullable=False, index=True
    )

    # Summary Scores
    business_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    contact_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    opportunity_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    lead_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)

    # Relationships
    source_records: Mapped[List["SourceRecord"]] = relationship("SourceRecord", back_populates="business", cascade="all, delete-orphan")
    website: Mapped[Optional["Website"]] = relationship("Website", back_populates="business", uselist=False, cascade="all, delete-orphan")
    social_profiles: Mapped[List["SocialProfile"]] = relationship("SocialProfile", back_populates="business", cascade="all, delete-orphan")
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="business", cascade="all, delete-orphan")
    website_audit: Mapped[Optional["WebsiteAudit"]] = relationship("WebsiteAudit", back_populates="business", uselist=False, cascade="all, delete-orphan")
    seo_audit: Mapped[Optional["SEOAudit"]] = relationship("SEOAudit", back_populates="business", uselist=False, cascade="all, delete-orphan")
    opportunities: Mapped[List["Opportunity"]] = relationship("Opportunity", back_populates="business", cascade="all, delete-orphan")
    lead_scores: Mapped[List["LeadScore"]] = relationship("LeadScore", back_populates="business", cascade="all, delete-orphan")
    verification_results: Mapped[List["VerificationResult"]] = relationship("VerificationResult", back_populates="business", cascade="all, delete-orphan")
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="business", cascade="all, delete-orphan")
    review_actions: Mapped[List["ReviewAction"]] = relationship("ReviewAction", back_populates="business", cascade="all, delete-orphan")


class SourceRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "source_records"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="source_records")

    target_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("target_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )

    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
