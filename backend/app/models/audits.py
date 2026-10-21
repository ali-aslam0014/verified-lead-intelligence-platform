import uuid
from typing import Optional
from sqlalchemy import String, Boolean, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin


class WebsiteAudit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "website_audits"

    website_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("websites.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    website: Mapped["Website"] = relationship("Website", back_populates="website_audit")

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="website_audit")

    # Audit Status
    audit_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False, index=True)

    # Technical Checks
    https_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    responsive_mobile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cta_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contact_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    navigation_quality: Mapped[str] = mapped_column(String(50), default="UNKNOWN", nullable=False)
    broken_links_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trust_signals_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    schema_markup_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    response_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # PageSpeed Core Web Vitals (Mobile)
    pagespeed_mobile_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pagespeed_desktop_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    first_contentful_paint_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    largest_contentful_paint_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cumulative_layout_shift: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_blocking_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    speed_index_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Redesign Intelligence
    redesign_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    redesign_recommendation: Mapped[str] = mapped_column(String(30), default="UNKNOWN", nullable=False, index=True)
    # URGENT / RECOMMENDED / SEO_ONLY / UNKNOWN

    # Issues detected (list of signal dicts)
    issues: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # AI-generated sales pitch for this business
    sales_pitch: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Raw PageSpeed API response (cached)
    raw_pagespeed_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    service_coverage: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    location_coverage: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class SEOAudit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "seo_audits"

    website_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("websites.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    website: Mapped["Website"] = relationship("Website", back_populates="seo_audit")

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="seo_audit")

    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    headings_summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    indexable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    canonical_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sitemap_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    robots_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    image_alt_coverage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    schema_types: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    local_seo_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # SEO signal issues list
    issues: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
