import uuid
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.business import Business, SourceRecord
from app.models.verification import VerificationResult, Evidence
from app.models.enums import LifecycleStatus
from app.services.verification_engine import VerificationEngine
from app.tasks.verification_task import verify_business_async, verify_target_batch_async
from pydantic import BaseModel, ConfigDict

router = APIRouter()


class VerificationResultResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    check_type: str
    result: str
    confidence: float
    reason: Optional[str]
    evidence: dict
    source: str
    observed_at: str

    model_config = ConfigDict(from_attributes=True)


class EvidenceResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    source: str
    source_url_or_id: Optional[str]
    observed_at: str
    status: str
    evidence_type: str
    data: dict

    model_config = ConfigDict(from_attributes=True)


@router.get("/console/stats", summary="Get Verification Console Global Metrics")
async def get_verification_console_stats(db: AsyncSession = Depends(get_db)):
    """Retrieves system-wide lead verification metrics for the Verification Console UI."""
    stmt = select(Business.lifecycle_status, func.count(Business.id)).group_by(Business.lifecycle_status)
    res = await db.execute(stmt)
    status_counts = dict(res.all())

    verified_count = status_counts.get(LifecycleStatus.VERIFIED, 0)
    reverify_count = status_counts.get(LifecycleStatus.REVERIFY_REQUIRED, 0)
    human_review_count = status_counts.get(LifecycleStatus.HUMAN_REVIEW, 0)
    discovered_count = status_counts.get(LifecycleStatus.DISCOVERED, 0)

    # Count businesses with conflicts
    conflict_stmt = select(func.count(Business.id)).where(Business.lifecycle_status == LifecycleStatus.HUMAN_REVIEW)
    c_res = await db.execute(conflict_stmt)
    conflict_count = c_res.scalar() or 0

    return {
        "total_discovered": discovered_count,
        "total_verified": verified_count,
        "reverify_required": reverify_count,
        "human_review_required": human_review_count,
        "conflicting_records_count": conflict_count,
    }


@router.get("/businesses/{business_id}/summary", summary="Get Business Verification Summary")
async def get_business_verification_summary(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full verification summary for a business entity."""
    stmt = select(Business).where(Business.id == business_id)
    res = await db.execute(stmt)
    business = res.scalar_one_or_none()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business entity with ID '{business_id}' was not found."
        )

    # Fetch verification results
    vr_stmt = select(VerificationResult).where(VerificationResult.business_id == business_id).order_by(VerificationResult.created_at.asc())
    vr_res = await db.execute(vr_stmt)
    results = vr_res.scalars().all()

    return {
        "business_id": str(business.id),
        "name": business.name,
        "lifecycle_status": business.lifecycle_status.value,
        "verified_at": business.verified_at.isoformat() if business.verified_at else None,
        "summary": business.verification_summary or {},
        "check_results": [
            {
                "id": str(r.id),
                "check_type": r.check_type.value,
                "result": r.result.value,
                "confidence": r.confidence,
                "reason": r.reason,
                "evidence": r.evidence,
                "source": r.source,
                "observed_at": r.observed_at.isoformat(),
            }
            for r in results
        ]
    }


@router.post("/businesses/{business_id}/verify", summary="Trigger Business Verification Job")
async def trigger_business_verification(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Triggers synchronous/asynchronous verification pass for a single business entity."""
    stmt = select(Business).where(Business.id == business_id)
    res = await db.execute(stmt)
    business = res.scalar_one_or_none()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business entity with ID '{business_id}' was not found."
        )

    engine = VerificationEngine()
    result = await engine.verify_business(db, business_id)
    return result


@router.get("/businesses/{business_id}/results", response_model=List[VerificationResultResponse], summary="Get Verification Results List")
async def get_business_verification_results(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves list of all individual VerificationResult records for a business."""
    stmt = select(VerificationResult).where(VerificationResult.business_id == business_id).order_by(VerificationResult.created_at.asc())
    res = await db.execute(stmt)
    results = res.scalars().all()

    return [
        {
            "id": r.id,
            "business_id": r.business_id,
            "check_type": r.check_type.value,
            "result": r.result.value,
            "confidence": r.confidence,
            "reason": r.reason,
            "evidence": r.evidence,
            "source": r.source,
            "observed_at": r.observed_at.isoformat(),
        }
        for r in results
    ]


@router.get("/businesses/{business_id}/evidence", response_model=List[EvidenceResponse], summary="Get Raw Evidence Items List")
async def get_business_evidence(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves list of raw Evidence records for a business entity."""
    stmt = select(Evidence).where(Evidence.business_id == business_id).order_by(Evidence.created_at.asc())
    res = await db.execute(stmt)
    evidence_items = res.scalars().all()

    return [
        {
            "id": e.id,
            "business_id": e.business_id,
            "source": e.source,
            "source_url_or_id": e.source_url_or_id,
            "observed_at": e.observed_at.isoformat(),
            "status": e.status,
            "evidence_type": e.evidence_type.value,
            "data": e.data,
        }
        for e in evidence_items
    ]


@router.post("/targets/{target_id}/batch", summary="Trigger Batch Target Leads Verification")
async def trigger_target_batch_verification(
    target_id: uuid.UUID,
):
    """Dispatches background task to run batch verification across all leads for a target."""
    asyncio.create_task(verify_target_batch_async(target_id))
    return {
        "status": "QUEUED",
        "target_id": str(target_id),
        "message": f"Batch verification queue job dispatched for Target '{target_id}'."
    }
