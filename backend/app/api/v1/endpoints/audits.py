import uuid
import logging
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, ConfigDict

from app.core.database import get_db
from app.models.business import Business
from app.models.digital_presence import Website
from app.models.audits import WebsiteAudit, SEOAudit
from app.services.audit_engine import AuditEngine

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────

class AuditIssueSchema(BaseModel):
    code: str
    severity: str
    points: int = 0
    description: str


class WebsiteAuditResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    audit_status: str

    # Technical
    https_enabled: bool
    responsive_mobile: bool
    cta_visible: bool
    contact_visible: bool
    schema_markup_present: bool
    response_time_ms: float

    # PageSpeed
    pagespeed_mobile_score: Optional[int]
    pagespeed_desktop_score: Optional[int]
    first_contentful_paint_ms: Optional[float]
    largest_contentful_paint_ms: Optional[float]
    cumulative_layout_shift: Optional[float]
    total_blocking_time_ms: Optional[float]
    speed_index_ms: Optional[float]

    # Redesign Intelligence
    redesign_score: int
    redesign_recommendation: str
    issues: List[Dict[str, Any]]
    sales_pitch: Optional[str]

    created_at: Any
    updated_at: Any

    model_config = ConfigDict(from_attributes=True)


class AuditListItemResponse(BaseModel):
    """Lightweight summary for listing all audited businesses."""
    business_id: uuid.UUID
    business_name: str
    business_city: Optional[str]
    website_url: Optional[str]
    audit_status: str
    redesign_score: int
    redesign_recommendation: str
    pagespeed_mobile_score: Optional[int]
    pagespeed_desktop_score: Optional[int]
    https_enabled: bool
    responsive_mobile: bool
    issues_count: int
    sales_pitch: Optional[str]
    updated_at: Any

    model_config = ConfigDict(from_attributes=True)


class AuditTriggerResponse(BaseModel):
    message: str
    business_id: str
    website_url: str


# ─────────────────────────────────────────────
# Background Audit Runner
# ─────────────────────────────────────────────

async def _run_audit_background(business_id: uuid.UUID):
    """Full audit pipeline running in background."""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            # Fetch business with website
            stmt = (
                select(Business)
                .options(selectinload(Business.website))
                .where(Business.id == business_id)
            )
            result = await db.execute(stmt)
            business = result.scalar_one_or_none()

            if not business or not business.website:
                logger.warning(f"[AuditBG] No business/website for ID {business_id}")
                return

            website = business.website
            website_url = website.url

            logger.info(f"[AuditBG] Running audit for {business.name} — {website_url}")

            # Run audit engine
            engine = AuditEngine()
            audit_result = await engine.run_audit(
                website_url=website_url,
                business_name=business.name,
                city=business.city,
            )

            # Upsert WebsiteAudit
            existing_audit_stmt = select(WebsiteAudit).where(WebsiteAudit.website_id == website.id)
            existing_result = await db.execute(existing_audit_stmt)
            audit_obj = existing_result.scalar_one_or_none()

            if not audit_obj:
                audit_obj = WebsiteAudit(
                    website_id=website.id,
                    business_id=business.id,
                )
                db.add(audit_obj)

            # Set all fields
            audit_obj.audit_status = audit_result["audit_status"]
            audit_obj.https_enabled = audit_result["https_enabled"]
            audit_obj.responsive_mobile = audit_result["responsive_mobile"]
            audit_obj.cta_visible = audit_result["cta_visible"]
            audit_obj.contact_visible = audit_result["contact_visible"]
            audit_obj.schema_markup_present = audit_result["schema_markup_present"]
            audit_obj.response_time_ms = audit_result["response_time_ms"]
            audit_obj.pagespeed_mobile_score = audit_result["pagespeed_mobile_score"]
            audit_obj.pagespeed_desktop_score = audit_result["pagespeed_desktop_score"]
            audit_obj.first_contentful_paint_ms = audit_result["first_contentful_paint_ms"]
            audit_obj.largest_contentful_paint_ms = audit_result["largest_contentful_paint_ms"]
            audit_obj.cumulative_layout_shift = audit_result["cumulative_layout_shift"]
            audit_obj.total_blocking_time_ms = audit_result["total_blocking_time_ms"]
            audit_obj.speed_index_ms = audit_result["speed_index_ms"]
            audit_obj.raw_pagespeed_data = audit_result["raw_pagespeed_data"]
            audit_obj.redesign_score = audit_result["redesign_score"]
            audit_obj.redesign_recommendation = audit_result["redesign_recommendation"]
            audit_obj.issues = audit_result["issues"]
            audit_obj.sales_pitch = audit_result["sales_pitch"]

            # Upsert SEOAudit
            seo_data = audit_result.get("seo", {})
            existing_seo_stmt = select(SEOAudit).where(SEOAudit.website_id == website.id)
            existing_seo_result = await db.execute(existing_seo_stmt)
            seo_obj = existing_seo_result.scalar_one_or_none()

            if not seo_obj:
                seo_obj = SEOAudit(
                    website_id=website.id,
                    business_id=business.id,
                )
                db.add(seo_obj)

            seo_obj.title = seo_data.get("title", "")
            seo_obj.meta_description = seo_data.get("meta_description", "")
            seo_obj.headings_summary = {"h1_count": seo_data.get("h1_count", 0)}
            seo_obj.canonical_url = None
            seo_obj.robots_present = seo_data.get("robots_present", False)
            seo_obj.issues = seo_data.get("issues", [])

            await db.commit()
            logger.info(f"[AuditBG] Audit COMPLETED for {business.name}. Score: {audit_result['redesign_score']} — {audit_result['redesign_recommendation']}")

        except Exception as e:
            logger.error(f"[AuditBG] Audit FAILED for business {business_id}: {e}", exc_info=True)


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@router.post("/businesses/{business_id}/audit", response_model=AuditTriggerResponse, tags=["Audits"])
async def trigger_website_audit(
    business_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a full Website Audit for a business with a website.
    Runs asynchronously in the background.
    """
    stmt = (
        select(Business)
        .options(selectinload(Business.website))
        .where(Business.id == business_id)
    )
    result = await db.execute(stmt)
    business = result.scalar_one_or_none()

    if not business:
        raise HTTPException(status_code=404, detail="Business not found.")

    if not business.website:
        raise HTTPException(
            status_code=400,
            detail="This business has no website. Website Audit requires a website URL."
        )

    # Mark as pending
    existing_audit_stmt = select(WebsiteAudit).where(WebsiteAudit.website_id == business.website.id)
    existing_result = await db.execute(existing_audit_stmt)
    audit_obj = existing_result.scalar_one_or_none()

    if audit_obj:
        audit_obj.audit_status = "PENDING"
        await db.commit()

    background_tasks.add_task(_run_audit_background, business_id)

    return AuditTriggerResponse(
        message="Website audit started in background. Check back in 20-30 seconds.",
        business_id=str(business_id),
        website_url=business.website.url,
    )


@router.get("/businesses/{business_id}/audit", response_model=Optional[WebsiteAuditResponse], tags=["Audits"])
async def get_business_audit(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the latest audit result for a specific business."""
    stmt = (
        select(WebsiteAudit)
        .where(WebsiteAudit.business_id == business_id)
    )
    result = await db.execute(stmt)
    audit = result.scalar_one_or_none()

    if not audit:
        return None

    return audit


@router.get("/audits", tags=["Audits"])
async def list_all_audits(
    recommendation: Optional[str] = None,
    min_score: Optional[int] = None,
    limit: int = 200,
    db: AsyncSession = Depends(get_db),
):
    """
    List all businesses that have been audited.
    Filter by recommendation (URGENT / RECOMMENDED / SEO_ONLY / GOOD)
    or minimum redesign score.
    """
    stmt = (
        select(WebsiteAudit, Business, Website)
        .join(Business, WebsiteAudit.business_id == Business.id)
        .join(Website, WebsiteAudit.website_id == Website.id)
        .where(WebsiteAudit.audit_status == "COMPLETED")
        .order_by(WebsiteAudit.redesign_score.desc())
        .limit(limit)
    )

    if recommendation:
        stmt = stmt.where(WebsiteAudit.redesign_recommendation == recommendation.upper())
    if min_score is not None:
        stmt = stmt.where(WebsiteAudit.redesign_score >= min_score)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "audit_id": str(row.WebsiteAudit.id),
            "business_id": str(row.WebsiteAudit.business_id),
            "business_name": row.Business.name,
            "business_city": row.Business.city,
            "website_url": row.Website.url,
            "website_domain": row.Website.domain,
            "audit_status": row.WebsiteAudit.audit_status,
            "redesign_score": row.WebsiteAudit.redesign_score,
            "redesign_recommendation": row.WebsiteAudit.redesign_recommendation,
            "pagespeed_mobile_score": row.WebsiteAudit.pagespeed_mobile_score,
            "pagespeed_desktop_score": row.WebsiteAudit.pagespeed_desktop_score,
            "https_enabled": row.WebsiteAudit.https_enabled,
            "responsive_mobile": row.WebsiteAudit.responsive_mobile,
            "cta_visible": row.WebsiteAudit.cta_visible,
            "schema_markup_present": row.WebsiteAudit.schema_markup_present,
            "response_time_ms": row.WebsiteAudit.response_time_ms,
            "issues_count": len(row.WebsiteAudit.issues or []),
            "issues": row.WebsiteAudit.issues,
            "sales_pitch": row.WebsiteAudit.sales_pitch,
            "updated_at": str(row.WebsiteAudit.updated_at),
        }
        for row in rows
    ]
