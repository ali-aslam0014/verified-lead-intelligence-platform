import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from app.models.enums import TargetStatus, TargetRunStatus, OpportunityType, JobStatus


class FilterDefinition(BaseModel):
    min_revenue: Optional[float] = Field(None, ge=0, description="Minimum annual revenue requirement")
    max_revenue: Optional[float] = Field(None, ge=0, description="Maximum annual revenue limit")
    min_employees: Optional[int] = Field(None, ge=0, description="Minimum employee count")
    max_employees: Optional[int] = Field(None, ge=0, description="Maximum employee count")
    technologies: List[str] = Field(default_factory=list, description="Targeted technology stack tags")
    keywords: List[str] = Field(default_factory=list, description="Targeted business domain keywords")

    @field_validator("technologies", "keywords", mode="before")
    @classmethod
    def sanitize_tags(cls, v: Any) -> List[str]:
        if not isinstance(v, list):
            return []
        cleaned = []
        for tag in v:
            if isinstance(tag, str) and tag.strip():
                cleaned.append(tag.strip()[:100])
        return cleaned[:50]

    @model_validator(mode="after")
    def validate_min_max_ranges(self) -> "FilterDefinition":
        if self.min_revenue is not None and self.max_revenue is not None:
            if self.min_revenue > self.max_revenue:
                raise ValueError("min_revenue cannot be greater than max_revenue")
        if self.min_employees is not None and self.max_employees is not None:
            if self.min_employees > self.max_employees:
                raise ValueError("min_employees cannot be greater than max_employees")
        return self


class SourceConfiguration(BaseModel):
    enabled_sources: List[str] = Field(
        default_factory=lambda: ["google_places", "website_crawler", "social_discovery"],
        description="Active discovery source adapter identifiers"
    )
    max_results_limit: int = Field(100, ge=1, le=5000, description="Maximum discovery volume limit")
    rate_limit_per_minute: int = Field(60, ge=1, le=1000, description="Requests allowed per minute")
    timeout_seconds: float = Field(30.0, ge=1.0, le=300.0, description="Source adapter HTTP timeout in seconds")


class TargetCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255, description="Human readable target search title")
    niche: str = Field(..., min_length=2, max_length=100, description="Target industry niche")
    sub_niche: Optional[str] = Field(None, max_length=100, description="Optional sub-niche specialization")
    geography: str = Field(..., min_length=2, max_length=150, description="Target location or region")
    filters: FilterDefinition = Field(default_factory=FilterDefinition)
    opportunity_types: List[OpportunityType] = Field(..., description="Targeted sales opportunity types")
    source_configuration: SourceConfiguration = Field(default_factory=SourceConfiguration)

    @field_validator("opportunity_types")
    @classmethod
    def validate_opportunity_types(cls, v: List[OpportunityType]) -> List[OpportunityType]:
        if not v:
            raise ValueError("opportunity_types list cannot be empty")
        # Deduplicate while preserving order
        deduped = []
        for opp in v:
            if opp not in deduped:
                deduped.append(opp)
        return deduped


class TargetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    niche: Optional[str] = Field(None, min_length=2, max_length=100)
    sub_niche: Optional[str] = Field(None, max_length=100)
    geography: Optional[str] = Field(None, min_length=2, max_length=150)
    status: Optional[TargetStatus] = None
    filters: Optional[FilterDefinition] = None
    opportunity_types: Optional[List[OpportunityType]] = None
    source_configuration: Optional[SourceConfiguration] = None

    @field_validator("opportunity_types")
    @classmethod
    def validate_opportunity_types_optional(cls, v: Optional[List[OpportunityType]]) -> Optional[List[OpportunityType]]:
        if v is not None:
            if not v:
                raise ValueError("opportunity_types list cannot be empty")
            deduped = []
            for opp in v:
                if opp not in deduped:
                    deduped.append(opp)
            return deduped
        return v


class TargetResponse(BaseModel):
    id: uuid.UUID
    name: str
    niche: str
    sub_niche: Optional[str]
    geography: str
    status: TargetStatus
    filters: dict
    opportunity_types: list
    source_configuration: dict
    created_by_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TargetRunCreate(BaseModel):
    target_id: uuid.UUID


class TargetRunResponse(BaseModel):
    id: uuid.UUID
    target_id: uuid.UUID
    status: TargetRunStatus
    total_discovered: int
    total_verified: int
    total_qualified: int
    total_human_review: int
    total_outreach_ready: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_log: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
