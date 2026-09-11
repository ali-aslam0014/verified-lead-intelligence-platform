import asyncio
import httpx

async def main():
    target_id = "f8ced3c2-4afc-47a2-a395-ef8aafd3ebf2"
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Trigger fresh run
        print(f"--- Triggering Fresh Run for Target {target_id} ---")
        tr_resp = await client.post(f"http://localhost:8000/api/v1/targets/{target_id}/runs")
        run_data = tr_resp.json()
        run_id = run_data["id"]
        print("Run ID:", run_id, "Status:", run_data["status"])

        # Wait 4 seconds
        await asyncio.sleep(4)

        # Check status
        r_resp = await client.get(f"http://localhost:8000/api/v1/targets/{target_id}/runs/{run_id}")
        r_data = r_resp.json()
        print(f"\nRun ID: {r_data['id']} | Status: {r_data['status']} | Discovered: {r_data['total_discovered']} | Verified: {r_data['total_verified']}")

        # Fetch businesses by target_id filter
        b_resp = await client.get(f"http://localhost:8000/api/v1/businesses?target_id={target_id}")
        businesses = b_resp.json()
        print(f"\n--- Fetched {len(businesses)} Discovered Businesses for target_id={target_id} ---")
        for b in businesses:
            print(f" - {b['name']}")
            print(f"   Address: {b['address']} | Phone: {b['phone']}")
            print(f"   Has Website: {b['has_website']} | Domain: {b.get('website', {}).get('domain') if b.get('website') else 'NONE (HOT LEAD!)'}")
            print(f"   Rating: {b.get('rating')} ({b.get('review_count')} reviews)")
            print()

if __name__ == "__main__":
    asyncio.run(main())
