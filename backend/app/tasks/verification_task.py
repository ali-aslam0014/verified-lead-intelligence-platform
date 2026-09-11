import uuid
import logging
import asyncio
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.business import Business, SourceRecord
from app.models.target import TargetRun, Target
from app.services.verification_engine import VerificationEngine

logger = logging.getLogger(__name__)


async def verify_business_async(business_id: uuid.UUID) -> Dict[str, Any]:
    """
    Asynchronous task worker to verify a single business entity.
    Runs website, contact, social, and identity verification suites.
    """
    logger.info(f"Executing async verification worker for Business ID: {business_id}")
    async with AsyncSessionLocal() as db:
        engine = VerificationEngine()
        res = await engine.verify_business(db, business_id)
        return res


async def verify_target_batch_async(target_id: uuid.UUID) -> Dict[str, Any]:
    """
    Asynchronous task worker to run batch verification across all discovered
    businesses belonging to a Target campaign.
    """
    logger.info(f"Starting Batch Verification Worker for Target ID: {target_id}")

    async with AsyncSessionLocal() as db:
        # Find businesses associated with target_id via SourceRecord & TargetRun
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

        logger.info(f"Found {len(business_ids)} businesses to verify for Target ID '{target_id}'")

        engine = VerificationEngine()
        verified_count = 0
        reverify_count = 0
        human_review_count = 0

        for b_id in business_ids:
            try:
                res = await engine.verify_business(db, b_id)
                status = res.get("lifecycle_status")
                if status == "VERIFIED":
                    verified_count += 1
                elif status == "HUMAN_REVIEW":
                    human_review_count += 1
                else:
                    reverify_count += 1
            except Exception as exc:
                logger.error(f"Error executing batch verification for Business ID {b_id}: {exc}")

        return {
            "target_id": str(target_id),
            "total_processed": len(business_ids),
            "verified_count": verified_count,
            "reverify_count": reverify_count,
            "human_review_count": human_review_count,
        }
