import uuid
import logging
from typing import Dict, Any, List
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.business import Business, SourceRecord
from app.models.target import TargetRun, Target
from app.services.opportunity_engine import OpportunityEngine

logger = logging.getLogger(__name__)


async def analyze_business_opportunities_async(business_id: uuid.UUID) -> Dict[str, Any]:
    """
    Asynchronous task worker to run opportunity intelligence engine on a single business.
    """
    logger.info(f"Executing async opportunity worker for Business ID: {business_id}")
    async with AsyncSessionLocal() as db:
        engine = OpportunityEngine()
        res = await engine.analyze_business(db, business_id)
        return res


async def analyze_target_opportunities_async(target_id: uuid.UUID) -> Dict[str, Any]:
    """
    Asynchronous task worker to run batch opportunity analysis for all leads in a Target.
    """
    logger.info(f"Starting Batch Opportunity Task for Target ID: {target_id}")

    async with AsyncSessionLocal() as db:
        stmt = (
            select(Business)
            .join(SourceRecord, Business.id == SourceRecord.business_id)
            .join(TargetRun, SourceRecord.target_run_id == TargetRun.id)
            .where(TargetRun.target_id == target_id)
            .distinct()
        )
        result = await db.execute(stmt)
        businesses = result.scalars().all()
        business_ids = [b.id for b in businesses]

        engine = OpportunityEngine()
        total_opportunities_detected = 0

        for b_id in business_ids:
            try:
                res = await engine.analyze_business(db, b_id)
                total_opportunities_detected += res.get("opportunity_count", 0)
            except Exception as exc:
                logger.error(f"Error analyzing opportunities for Business ID {b_id}: {exc}")

        return {
            "target_id": str(target_id),
            "total_businesses_analyzed": len(business_ids),
            "total_opportunities_detected": total_opportunities_detected,
        }
