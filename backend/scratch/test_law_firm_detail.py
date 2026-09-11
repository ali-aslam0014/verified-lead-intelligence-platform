import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Get target runs for law firm target f8ced3c2-4afc-47a2-a395-ef8aafd3ebf2
        r_resp = await client.get("http://localhost:8000/api/v1/targets/f8ced3c2-4afc-47a2-a395-ef8aafd3ebf2/runs")
        runs = r_resp.json()
        print("--- Law Firm Target Runs ---")
        for r in runs:
            print(f"Run ID: {r['id']} | Status: {r['status']} | Discovered: {r['total_discovered']} | Verified: {r['total_verified']}")

        # Get business detail or source records for the latest run
        if runs:
            run_id = runs[0]['id']
            # Fetch source records
            b_resp = await client.get("http://localhost:8000/api/v1/businesses")
            all_b = b_resp.json()
            print(f"\n--- Checking {len(all_b)} businesses in DB ---")
            for b in all_b:
                d_resp = await client.get(f"http://localhost:8000/api/v1/businesses/{b['id']}")
                detail = d_resp.json()
                srs = detail.get("source_records", [])
                for sr in srs:
                    print(f"Business: '{b['name']}' | City: '{b['city']}' | SR TargetRun: {sr.get('target_run_id')} | SR Source: {sr.get('source_name')}")

if __name__ == "__main__":
    asyncio.run(main())
