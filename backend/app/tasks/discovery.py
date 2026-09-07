import uuid
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.target import TargetRun, Target
from app.models.enums import TargetRunStatus
from app.sources.base import DiscoveryRequest
from app.sources.google_places import GooglePlacesAdapter, GooglePlacesAPIError
from app.sources.website_enrichment import WebsiteEnrichmentAdapter
from app.services.resolver import BusinessResolver

logger = logging.getLogger(__name__)


async def execute_discovery_run_async(target_run_id: uuid.UUID) -> Dict[str, Any]:
    """
    Asynchronous discovery execution worker.
    Reads target definition, queries Google Places API (New), stores verbatim SourceRecord provenance,
    runs BusinessResolver deduplication, and updates TargetRun status.
    """
    logger.info(f"Starting Discovery Engine execution for TargetRun ID: {target_run_id}")

    async with AsyncSessionLocal() as db:
        # Load TargetRun & Parent Target
        stmt = (
            select(TargetRun)
            .where(TargetRun.id == target_run_id)
            .options(selectinload(TargetRun.target))
        )
        res = await db.execute(stmt)
        target_run = res.scalar_one_or_none()

        if not target_run or not target_run.target:
            logger.error(f"TargetRun ID '{target_run_id}' or parent Target not found.")
            return {"status": "FAILED", "error": "TargetRun or parent Target not found"}

        target = target_run.target

        # Set status to RUNNING
        target_run.status = TargetRunStatus.RUNNING
        target_run.started_at = datetime.now(timezone.utc)
        await db.commit()

        try:
            # 1. Primary Discovery: Google Places API
            places_adapter = GooglePlacesAdapter()
            request = DiscoveryRequest(
                niche=target.niche,
                geography=target.geography,
                sub_niche=target.sub_niche,
                filters=target.filters or {},
                source_configuration=target.source_configuration or {},
            )

            raw_results = await places_adapter.search(request)

            # 2. Entity Resolution & Deduplication
            resolver = BusinessResolver()
            total_discovered = len(raw_results)
            total_unique_businesses = 0
            duplicates_merged = 0

            website_enrichment_adapter = WebsiteEnrichmentAdapter()

            for raw_res in raw_results:
                business, is_new = await resolver.resolve_record(
                    db=db,
                    raw_result=raw_res,
                    target_run_id=target_run.id
                )
                if is_new:
                    total_unique_businesses += 1
                else:
                    duplicates_merged += 1

                # 3. Secondary Enrichment: Website Domain Probe (only if domain exists)
                website_url = raw_res.raw_data.get("website")
                if website_url and is_new:
                    try:
                        await website_enrichment_adapter.enrich_url(website_url)
                    except Exception as e:
                        logger.warning(f"Secondary website enrichment error for {website_url}: {e}")

            await db.commit()

            # Update TargetRun status to COMPLETED
            target_run.status = TargetRunStatus.COMPLETED
            target_run.completed_at = datetime.now(timezone.utc)
            target_run.total_discovered = total_discovered
            target_run.total_verified = total_unique_businesses # Unique canonical businesses
            target_run.error_log = {
                "raw_api_results": total_discovered,
                "unique_businesses_created": total_unique_businesses,
                "duplicates_merged": duplicates_merged,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.commit()

            logger.info(
                f"Discovery Run '{target_run_id}' COMPLETED: Discovered={total_discovered}, "
                f"Unique={total_unique_businesses}, DuplicatesMerged={duplicates_merged}"
            )

            return {
                "status": "COMPLETED",
                "total_discovered": total_discovered,
                "unique_businesses": total_unique_businesses,
                "duplicates_merged": duplicates_merged,
            }

        except GooglePlacesAPIError as g_err:
            logger.error(f"Google Places API Error during discovery run '{target_run_id}': {g_err}")
            target_run.status = TargetRunStatus.FAILED
            target_run.completed_at = datetime.now(timezone.utc)
            target_run.error_log = {
                "error_type": "GooglePlacesAPIError",
                "message": str(g_err),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await db.commit()
            return {"status": "FAILED", "error": str(g_err)}

        except Exception as exc:
            logger.exception(f"Unexpected error executing discovery run '{target_run_id}': {exc}")
            target_run.status = TargetRunStatus.FAILED
            target_run.completed_at = datetime.now(timezone.utc)
            target_run.error_log = {
                "error_type": type(exc).__name__,
                "message": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await db.commit()
            return {"status": "FAILED", "error": str(exc)}
