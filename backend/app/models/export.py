import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import ExportFormat


class Export(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exports"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    format: Mapped[ExportFormat] = mapped_column(
        SQLEnum(ExportFormat, name="export_format_enum"), default=ExportFormat.CSV, nullable=False
    )
    filters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    lead_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)

    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
