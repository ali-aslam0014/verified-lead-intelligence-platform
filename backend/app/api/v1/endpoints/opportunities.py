import uuid
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.business import Business
from app.models.opportunity import Opportunity
from app.models.verification import Evidence
from app.services.opportunity_engine import OpportunityEngine
from app.tasks.opportunities import analyze_business_opportunities_async, analyze_target_opportunities_async
from pydantic import BaseModel, ConfigDict

router = APIRouter()


class OpportunityResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    type: str
    status: str
    priority: str
    confidence: float
    recommended_service: str
    recommended_angle: Optional[str]
    reason: str
    evidence: dict
    evidence_ids: dict
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class OpportunityReviewPayload(BaseModel):
    status: str  # CONFIRMED, REJECTED, NEEDS_REVIEW
    notes: Optional[str] = None


@router.get("/businesses/{business_id}/opportunities", response_model=List[OpportunityResponse], summary="List Business Opportunities")
async def list_business_opportunities(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves list of detected/confirmed sales opportunities for a business."""
    stmt = select(Opportunity).where(Opportunity.business_id == business_id).order_by(Opportunity.confidence.desc())
    res = await db.execute(stmt)
    opps = res.scalars().all()

    return [
        {
            "id": o.id,
            "business_id": o.business_id,
            "type": o.type.value,
            "status": o.status,
            "priority": o.priority,
            "confidence": o.confidence,
            "recommended_service": o.recommended_service,
            "recommended_angle": o.recommended_angle,
            "reason": o.reason,
            "evidence": o.evidence,
            "evidence_ids": o.evidence_ids,
            "created_at": o.created_at.isoformat(),
        }
        for o in opps
    ]


@router.post("/businesses/{business_id}/opportunities/analyze", summary="Trigger Business Opportunity Analysis")
async def trigger_business_opportunity_analysis(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Triggers Opportunity Intelligence Engine analysis on a business."""
    stmt = select(Business).where(Business.id == business_id)
    res = await db.execute(stmt)
    business = res.scalar_one_or_none()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business entity with ID '{business_id}' was not found."
        )

    engine = OpportunityEngine()
    result = await engine.analyze_business(db, business_id)
    return result


@router.post("/targets/{target_id}/opportunities/analyze", summary="Trigger Batch Target Opportunity Analysis")
async def trigger_target_opportunity_analysis(
    target_id: uuid.UUID
):
    """Dispatches background task to run opportunity analysis across all verified leads in a Target."""
    asyncio.create_task(analyze_target_opportunities_async(target_id))
    return {
        "status": "QUEUED",
        "target_id": str(target_id),
        "message": f"Batch opportunity analysis worker task dispatched for Target '{target_id}'."
    }


@router.get("/{opportunity_id}", response_model=OpportunityResponse, summary="Get Opportunity Detail")
async def get_opportunity_detail(
    opportunity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves detailed record for an Opportunity."""
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    res = await db.execute(stmt)
    opp = res.scalar_one_or_none()

    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity with ID '{opportunity_id}' was not found."
        )

    return {
        "id": opp.id,
        "business_id": opp.business_id,
        "type": opp.type.value,
        "status": opp.status,
        "priority": opp.priority,
        "confidence": opp.confidence,
        "recommended_service": opp.recommended_service,
        "recommended_angle": opp.recommended_angle,
        "reason": opp.reason,
        "evidence": opp.evidence,
        "evidence_ids": opp.evidence_ids,
        "created_at": opp.created_at.isoformat(),
    }


@router.get("/{opportunity_id}/evidence", summary="Get Opportunity Evidence List")
async def get_opportunity_evidence(
    opportunity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves supporting Evidence records linked to an Opportunity."""
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    res = await db.execute(stmt)
    opp = res.scalar_one_or_none()

    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity with ID '{opportunity_id}' was not found."
        )

    # Fetch evidence items linked to business
    ev_stmt = select(Evidence).where(Evidence.business_id == opp.business_id).order_by(Evidence.created_at.asc())
    ev_res = await db.execute(ev_stmt)
    ev_items = ev_res.scalars().all()

    return [
        {
            "id": str(e.id),
            "source": e.source,
            "source_url_or_id": e.source_url_or_id,
            "observed_at": e.observed_at.isoformat(),
            "status": e.status,
            "evidence_type": e.evidence_type.value,
            "data": e.data,
        }
        for e in ev_items
    ]


@router.post("/{opportunity_id}/review", summary="Review Opportunity Candidate")
async def review_opportunity(
    opportunity_id: uuid.UUID,
    payload: OpportunityReviewPayload,
    db: AsyncSession = Depends(get_db)
):
    """Updates opportunity review status (CONFIRMED, REJECTED, NEEDS_REVIEW)."""
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    res = await db.execute(stmt)
    opp = res.scalar_one_or_none()

    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity with ID '{opportunity_id}' was not found."
        )

    opp.status = payload.status
    await db.commit()
    await db.refresh(opp)

    return {
        "id": str(opp.id),
        "status": opp.status,
        "message": f"Opportunity updated to status '{opp.status}'."
    }
