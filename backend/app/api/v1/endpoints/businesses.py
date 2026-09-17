import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.business import Business, SourceRecord
from app.models.digital_presence import Website, Contact
from app.models.enums import LifecycleStatus
from pydantic import BaseModel, ConfigDict

router = APIRouter()


class WebsiteSchema(BaseModel):
    id: uuid.UUID
    url: str
    domain: str
    status: str
    model_config = ConfigDict(from_attributes=True)


class ContactSchema(BaseModel):
    id: uuid.UUID
    type: str
    value: str
    normalized_value: str
    validity_status: str
    confidence: float
    model_config = ConfigDict(from_attributes=True)


class SourceRecordSchema(BaseModel):
    id: uuid.UUID
    source_name: str
    source_identifier: str
    raw_data: dict
    observed_at: str
    model_config = ConfigDict(from_attributes=True)


class BusinessResponse(BaseModel):
    id: uuid.UUID
    name: str
    normalized_name: str
    category: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    phone: Optional[str]
    lifecycle_status: str
    business_confidence: float
    website: Optional[WebsiteSchema] = None
    has_website: bool = False
    rating: Optional[float] = None
    review_count: Optional[int] = None
    social_links: dict = {}
    opportunity_signals: List[str] = []
    contacts: List[ContactSchema] = []
    source_records_count: int = 0
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class BusinessDetailResponse(BusinessResponse):
    source_records: List[dict] = []


@router.get("", response_model=List[BusinessResponse], summary="List Discovered Businesses")
async def list_businesses(
    skip: int = Query(0, ge=0, description="Offset pagination skip count"),
    limit: int = Query(100, ge=1, le=500, description="Page size limit"),
    search: Optional[str] = Query(None, description="Search by business name, city, or phone"),
    city: Optional[str] = Query(None, description="Filter by city"),
    target_id: Optional[uuid.UUID] = Query(None, description="Filter leads by parent Target Campaign ID"),
    has_website: Optional[bool] = Query(None, description="Filter by website availability"),
    status: Optional[LifecycleStatus] = Query(None, description="Filter by lifecycle status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves paginated list of canonical Business entities.
    Returns discovered lead records with website domain links and source counts.
    Supports filtering by target_id, city, search term, and website status.
    """
    from app.models.target import TargetRun

    query = (
        select(Business)
        .options(
            selectinload(Business.website),
            selectinload(Business.contacts),
            selectinload(Business.source_records),
        )
    )

    if target_id:
        subq = (
            select(SourceRecord.business_id)
            .join(TargetRun, SourceRecord.target_run_id == TargetRun.id)
            .where(TargetRun.target_id == target_id)
        )
        query = query.where(Business.id.in_(subq))

    if status:
        query = query.where(Business.lifecycle_status == status)

    if city:
        clean_city = city.split(",")[0].strip()
        if clean_city:
            query = query.where(
                or_(
                    Business.city.ilike(f"%{clean_city}%"),
                    Business.address.ilike(f"%{clean_city}%"),
                )
            )

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                Business.name.ilike(search_pattern),
                Business.city.ilike(search_pattern),
                Business.address.ilike(search_pattern),
                Business.phone.ilike(search_pattern),
            )
        )

    query = query.order_by(Business.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    businesses = result.scalars().all()

    response_items = []
    for b in businesses:
        latest_sr_data = b.source_records[0].raw_data if b.source_records else {}
        b_has_website = bool(b.website or latest_sr_data.get("has_website") or latest_sr_data.get("website"))
        
        if has_website is not None and b_has_website != has_website:
            continue

        b_dict = {
            "id": b.id,
            "name": b.name,
            "normalized_name": b.normalized_name,
            "category": b.category,
            "address": b.address,
            "city": b.city,
            "state": b.state,
            "country": b.country,
            "postal_code": b.postal_code,
            "phone": b.phone or latest_sr_data.get("phone"),
            "lifecycle_status": b.lifecycle_status.value,
            "business_confidence": b.business_confidence,
            "website": {
                "id": b.website.id,
                "url": b.website.url,
                "domain": b.website.domain,
                "status": b.website.status.value,
            } if b.website else None,
            "has_website": b_has_website,
            "rating": latest_sr_data.get("rating"),
            "review_count": latest_sr_data.get("review_count") or latest_sr_data.get("user_rating_count"),
            "social_links": latest_sr_data.get("social_links") or {},
            "opportunity_signals": latest_sr_data.get("opportunity_signals") or (["NO_WEBSITE"] if not b_has_website else []),
            "contacts": [
                {
                    "id": c.id,
                    "type": c.type.value,
                    "value": c.value,
                    "normalized_value": c.normalized_value,
                    "validity_status": c.validity_status,
                    "confidence": c.confidence,
                } for c in b.contacts
            ],
            "source_records_count": len(b.source_records),
            "created_at": b.created_at.isoformat(),
            "updated_at": b.updated_at.isoformat(),
        }
        response_items.append(b_dict)

    return response_items


@router.get("/{business_id}", response_model=BusinessDetailResponse, summary="Get Discovered Business Detail & Raw Provenance")
async def get_business_detail(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves complete canonical Business entity by ID, including
    verbatim SourceRecord JSON payload provenance audit history.
    """
    query = (
        select(Business)
        .where(Business.id == business_id)
        .options(
            selectinload(Business.website),
            selectinload(Business.contacts),
            selectinload(Business.source_records),
        )
    )
    result = await db.execute(query)
    b = result.scalar_one_or_none()

    if not b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business entity with ID '{business_id}' was not found."
        )

    source_records_list = [
        {
            "id": str(sr.id),
            "source_name": sr.source_name,
            "source_identifier": sr.source_identifier,
            "raw_data": sr.raw_data,
            "observed_at": sr.observed_at.isoformat(),
        }
        for sr in b.source_records
    ]

    latest_sr_data = b.source_records[0].raw_data if b.source_records else {}
    b_has_website = bool(b.website or latest_sr_data.get("has_website") or latest_sr_data.get("website"))

    return {
        "id": b.id,
        "name": b.name,
        "normalized_name": b.normalized_name,
        "category": b.category,
        "address": b.address,
        "city": b.city,
        "state": b.state,
        "country": b.country,
        "postal_code": b.postal_code,
        "phone": b.phone or latest_sr_data.get("phone"),
        "lifecycle_status": b.lifecycle_status.value,
        "business_confidence": b.business_confidence,
        "website": {
            "id": b.website.id,
            "url": b.website.url,
            "domain": b.website.domain,
            "status": b.website.status.value,
        } if b.website else None,
        "has_website": b_has_website,
        "rating": latest_sr_data.get("rating"),
        "review_count": latest_sr_data.get("review_count") or latest_sr_data.get("user_rating_count"),
        "social_links": latest_sr_data.get("social_links") or {},
        "opportunity_signals": latest_sr_data.get("opportunity_signals") or (["NO_WEBSITE"] if not b_has_website else []),
        "contacts": [
            {
                "id": c.id,
                "type": c.type.value,
                "value": c.value,
                "normalized_value": c.normalized_value,
                "validity_status": c.validity_status,
                "confidence": c.confidence,
            } for c in b.contacts
        ],
        "source_records_count": len(b.source_records),
        "source_records": source_records_list,
        "created_at": b.created_at.isoformat(),
        "updated_at": b.updated_at.isoformat(),
    }
