import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import WebsiteStatus, SocialPlatform, SocialStatus, ContactType


class Website(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "websites"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="website")

    url: Mapped[str] = mapped_column(String(500), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    status: Mapped[WebsiteStatus] = mapped_column(
        SQLEnum(WebsiteStatus, name="website_status_enum"), default=WebsiteStatus.UNCERTAIN, nullable=False, index=True
    )
    ownership_signal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    website_audit: Mapped[Optional["WebsiteAudit"]] = relationship("WebsiteAudit", back_populates="website", uselist=False)
    seo_audit: Mapped[Optional["SEOAudit"]] = relationship("SEOAudit", back_populates="website", uselist=False)


class SocialProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "social_profiles"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="social_profiles")

    platform: Mapped[SocialPlatform] = mapped_column(
        SQLEnum(SocialPlatform, name="social_platform_enum"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    identity_match_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    activity_status: Mapped[SocialStatus] = mapped_column(
        SQLEnum(SocialStatus, name="social_status_enum"), default=SocialStatus.FOUND_UNVERIFIED, nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Contact(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contacts"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="contacts")

    type: Mapped[ContactType] = mapped_column(
        SQLEnum(ContactType, name="contact_type_enum"), nullable=False, index=True
    )
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    validity_status: Mapped[str] = mapped_column(String(50), default="UNKNOWN", nullable=False)
    ownership_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
