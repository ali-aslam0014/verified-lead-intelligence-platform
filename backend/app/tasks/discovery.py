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
from app.sources.live_google_places import LiveGooglePlacesAdapter
from app.sources.google_places import GooglePlacesAdapter, GooglePlacesAPIError
from app.sources.website_enrichment import WebsiteEnrichmentAdapter
from app.services.resolver import BusinessResolver

logger = logging.getLogger(__name__)


async def execute_discovery_run_async(target_run_id: uuid.UUID) -> Dict[str, Any]:
    """
    Asynchronous discovery execution worker.
    Reads target definition, queries Live Google Places / Search engine,
    stores verbatim SourceRecord provenance, runs BusinessResolver deduplication,
    and updates TargetRun status.
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
            request = DiscoveryRequest(
                niche=target.niche,
                geography=target.geography,
                sub_niche=target.sub_niche,
                filters=target.filters or {},
                source_configuration=target.source_configuration or {},
            )

            enabled_sources = target.source_configuration.get("enabled_sources", [])
            
            from app.sources.yelp import YelpAdapter

            raw_results = []
            
            # 1. Attempt Google Places if enabled and configured
            if "google_places" in enabled_sources:
                try:
                    places_adapter = GooglePlacesAdapter()
                    raw_results = await places_adapter.search(request)
                except Exception as exc:
                    logger.warning(f"Google Places API adapter skipped or failed: {exc}. Falling back to Yelp Direct Directory.")

            # 2. If Google Places returned no results, try Yelp Direct Directory
            if not raw_results:
                try:
                    yelp_adapter = YelpAdapter()
                    raw_results = await yelp_adapter.search(request)
                except Exception as exc:
                    logger.warning(f"Yelp adapter search failed: {exc}. Falling back to Live Search Directory.")

            # 3. Fallback to Live Search Directory Engine
            if not raw_results:
                live_adapter = LiveGooglePlacesAdapter()
                raw_results = await live_adapter.search(request)

            # 2. Entity Resolution & Deduplication
            resolver = BusinessResolver()
            total_discovered = len(raw_results)
            total_unique_businesses = 0
            duplicates_merged = 0

            websites_to_enrich = []
            for raw_res in raw_results:
                business, is_new = await resolver.resolve_record(
                    db=db,
                    raw_result=raw_res,
                    target_run_id=target_run.id
                )
                if is_new:
                    total_unique_businesses += 1
                    website_url = raw_res.raw_data.get("website")
                    if website_url:
                        websites_to_enrich.append((raw_res, website_url))
                else:
                    duplicates_merged += 1

            # 3. Fast Concurrent Secondary Enrichment (website probes in parallel)
            if websites_to_enrich:
                website_enrichment_adapter = WebsiteEnrichmentAdapter()
                
                async def probe_single(raw_res_obj, url):
                    try:
                        enrich_res = await asyncio.wait_for(
                            website_enrichment_adapter.enrich_url(url), 
                            timeout=1.5
                        )
                        extracted_socials = enrich_res.raw_data.get("social_links", {})
                        if extracted_socials:
                            existing_socials = raw_res_obj.raw_data.get("social_links") or {}
                            existing_socials.update(extracted_socials)
                            raw_res_obj.raw_data["social_links"] = existing_socials
                    except Exception as e:
                        logger.debug(f"Fast website probe skipped for {url}: {e}")

                probe_tasks = [probe_single(res_obj, url) for res_obj, url in websites_to_enrich[:15]]
                await asyncio.gather(*probe_tasks, return_exceptions=True)

            await db.commit()

            # Update TargetRun status to COMPLETED
            # Total verified is total valid canonical businesses resolved/associated with this run
            total_verified_leads = total_unique_businesses + duplicates_merged

            target_run.status = TargetRunStatus.COMPLETED
            target_run.completed_at = datetime.now(timezone.utc)
            target_run.total_discovered = total_discovered
            target_run.total_verified = total_verified_leads
            target_run.error_log = {
                "raw_api_results": total_discovered,
                "unique_businesses_created": total_unique_businesses,
                "duplicates_merged": duplicates_merged,
                "total_verified_leads": total_verified_leads,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.commit()

            logger.info(
                f"Discovery Run '{target_run_id}' COMPLETED: Discovered={total_discovered}, "
                f"Verified={total_verified_leads} (New={total_unique_businesses}, Merged={duplicates_merged})"
            )

            return {
                "status": "COMPLETED",
                "total_discovered": total_discovered,
                "total_verified": total_verified_leads,
                "unique_businesses": total_unique_businesses,
                "duplicates_merged": duplicates_merged,
            }

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
