import uuid
from typing import Optional
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, JSON
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

    https_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    responsive_mobile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cta_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contact_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    navigation_quality: Mapped[str] = mapped_column(String(50), default="UNKNOWN", nullable=False)
    broken_links_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trust_signals_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

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
