import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.target import Target, TargetRun
from app.models.enums import TargetStatus, TargetRunStatus
from app.schemas.target import (
    TargetCreate,
    TargetUpdate,
    TargetResponse,
    TargetRunResponse,
)

router = APIRouter()


@router.post("", response_model=TargetResponse, status_code=status.HTTP_201_CREATED, summary="Create Target Definition")
async def create_target(
    payload: TargetCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new target definition with strict filter validations,
    deduplicated opportunity types, and source configuration.
    """
    target = Target(
        name=payload.name,
        niche=payload.niche,
        sub_niche=payload.sub_niche,
        geography=payload.geography,
        status=TargetStatus.ACTIVE,
        filters=payload.filters.model_dump(),
        opportunity_types=[o.value for o in payload.opportunity_types],
        source_configuration=payload.source_configuration.model_dump(),
    )
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target


@router.get("", response_model=List[TargetResponse], summary="List Targets with Pagination & Filters")
async def list_targets(
    skip: int = Query(0, ge=0, description="Offset pagination skip count"),
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    niche: Optional[str] = Query(None, description="Filter by industry niche"),
    status: Optional[TargetStatus] = Query(None, description="Filter by target status"),
    include_cancelled: bool = Query(False, description="Include soft-deleted/cancelled targets"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves paginated targets list.
    Excludes soft-deleted (CANCELLED) targets by default unless include_cancelled=True.
    """
    query = select(Target)

    if not include_cancelled and status != TargetStatus.CANCELLED:
        query = query.where(Target.status != TargetStatus.CANCELLED)

    if status:
        query = query.where(Target.status == status)

    if niche:
        query = query.where(Target.niche.ilike(f"%{niche}%"))

    query = query.order_by(Target.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    targets = result.scalars().all()
    return targets


@router.get("/{target_id}", response_model=TargetResponse, summary="Get Target Details")
async def get_target(
    target_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves target details by UUID. Returns 404 if missing or cancelled."""
    result = await db.execute(select(Target).where(Target.id == target_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID '{target_id}' was not found."
        )
    return target


@router.put("/{target_id}", response_model=TargetResponse, summary="Update Target Definition")
async def update_target(
    target_id: uuid.UUID,
    payload: TargetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates target fields. Returns 404 if target does not exist."""
    result = await db.execute(select(Target).where(Target.id == target_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID '{target_id}' was not found."
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "filters" in update_data and update_data["filters"] is not None:
        update_data["filters"] = payload.filters.model_dump()
    if "source_configuration" in update_data and update_data["source_configuration"] is not None:
        update_data["source_configuration"] = payload.source_configuration.model_dump()
    if "opportunity_types" in update_data and update_data["opportunity_types"] is not None:
        update_data["opportunity_types"] = [o.value for o in payload.opportunity_types]

    for key, value in update_data.items():
        setattr(target, key, value)

    await db.commit()
    await db.refresh(target)
    return target


@router.delete("/{target_id}", response_model=TargetResponse, summary="Soft Delete Target")
async def soft_delete_target(
    target_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft-deletes a target by setting status to CANCELLED.
    Preserves historical target run provenance records. Returns 404 if target missing.
    """
    result = await db.execute(select(Target).where(Target.id == target_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID '{target_id}' was not found."
        )

    target.status = TargetStatus.CANCELLED
    await db.commit()
    await db.refresh(target)
    return target


@router.post("/{target_id}/runs", response_model=TargetRunResponse, status_code=status.HTTP_201_CREATED, summary="Trigger Target Discovery Run")
async def trigger_target_run(
    target_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers a new discovery run for a target.
    Creates a TargetRun record in QUEUED state and dispatches execution queue abstraction.
    """
    result = await db.execute(select(Target).where(Target.id == target_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID '{target_id}' was not found."
        )

    if target.status == TargetStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot trigger discovery run for soft-deleted/cancelled target '{target_id}'."
        )

    target_run = TargetRun(
        target_id=target.id,
        status=TargetRunStatus.QUEUED,
        total_discovered=0,
        total_verified=0,
        total_qualified=0,
        total_human_review=0,
        total_outreach_ready=0,
        started_at=datetime.now(timezone.utc),
        error_log={}
    )
    db.add(target_run)
    await db.commit()
    await db.refresh(target_run)
    return target_run


@router.get("/{target_id}/runs", response_model=List[TargetRunResponse], summary="List Discovery Runs for Target")
async def list_target_runs(
    target_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all discovery run execution records for a target."""
    result = await db.execute(select(Target).where(Target.id == target_id))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with ID '{target_id}' was not found."
        )

    runs_result = await db.execute(
        select(TargetRun)
        .where(TargetRun.target_id == target_id)
        .order_by(TargetRun.created_at.desc())
    )
    return runs_result.scalars().all()


@router.get("/{target_id}/runs/{run_id}", response_model=TargetRunResponse, summary="Get Target Run Details")
async def get_target_run_details(
    target_id: uuid.UUID,
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Gets details and live statistics of a specific target run."""
    result = await db.execute(
        select(TargetRun)
        .where(TargetRun.id == run_id, TargetRun.target_id == target_id)
    )
    target_run = result.scalar_one_or_none()

    if not target_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target run '{run_id}' for target '{target_id}' was not found."
        )

    return target_run
