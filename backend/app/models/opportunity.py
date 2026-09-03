import uuid
from typing import Optional
from sqlalchemy import String, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import OpportunityType


class Opportunity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "opportunities"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="opportunities")

    type: Mapped[OpportunityType] = mapped_column(
        SQLEnum(OpportunityType, name="opportunity_type_enum"), nullable=False, index=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recommended_service: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)


class LeadScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lead_scores"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business: Mapped["Business"] = relationship("Business", back_populates="lead_scores")

    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    business_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    contact_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    opportunity_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    lead_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    rules_applied: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
