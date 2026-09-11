import asyncio
import httpx

API_BASE = "http://localhost:8000/api/v1"

async def test_dentist_run():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Create Target Definition for Dentist in New York
        target_payload = {
            "name": "Dentist in New York Real Yelp Test",
            "niche": "dentist",
            "sub_niche": None,
            "geography": "New York, NY",
            "filters": {"has_website": None, "min_rating": 3.5, "min_reviews": 5},
            "opportunity_types": ["NEW_WEBSITE", "LOCAL_SEO"],
            "source_configuration": {
                "max_results_limit": 10,
                "enabled_sources": ["google_places", "yelp", "live_google_places"]
            }
        }
        
        print("Creating target 'dentist in New York'...")
        res = await client.post(f"{API_BASE}/targets", json=target_payload)
        assert res.status_code == 201, f"Failed to create target: {res.text}"
        target = res.json()
        target_id = target["id"]
        print(f"Target Created! ID: {target_id}")

        # 2. Trigger Discovery Run
        print(f"Triggering Discovery Run for target_id={target_id}...")
        res = await client.post(f"{API_BASE}/targets/{target_id}/runs")
        assert res.status_code == 201, f"Failed to trigger run: {res.text}"
        run_data = res.json()
        run_id = run_data["id"]
        print(f"Run Triggered! Run ID: {run_id} | Status: {run_data['status']}")

        # 3. Poll status until COMPLETED or FAILED
        for _ in range(20):
            await asyncio.sleep(1.0)
            res = await client.get(f"{API_BASE}/targets/{target_id}/runs/{run_id}")
            run_status = res.json()
            status = run_status["status"]
            print(f"  Polling Run Status: {status} (Discovered: {run_status['total_discovered']}, Verified: {run_status['total_verified']})")
            if status in ["COMPLETED", "FAILED"]:
                break

        assert run_status["status"] == "COMPLETED", f"Run failed! Log: {run_status.get('error_log')}"

        # 4. Fetch Businesses for this target
        res = await client.get(f"{API_BASE}/businesses?target_id={target_id}")
        assert res.status_code == 200, f"Failed to fetch businesses: {res.text}"
        businesses = res.json()
        print(f"\n--- Fetched {len(businesses)} Real Dentist Leads for Target '{target['name']}' ---")

        for idx, biz in enumerate(businesses, 1):
            print(f"{idx}. {biz['name']}")
            print(f"   Address: {biz['address']} | Phone: {biz['phone']}")
            print(f"   Website: {biz['website']} | Has Website: {biz['has_website']}")
            print(f"   Rating: {biz['rating']} ({biz['user_rating_count']} reviews)")
            print(f"   Socials: {biz['social_links']}")
            print(f"   Opportunity Signals: {biz['opportunity_signals']}\n")

if __name__ == "__main__":
    asyncio.run(test_dentist_run())
