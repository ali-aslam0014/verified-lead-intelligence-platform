import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Check source records for run 3a7de31e-66a2-4529-9891-341e4f7cda30 and e7b74cfc-2a67-463c-b30f-164ba258071d
        run_id_1 = "3a7de31e-66a2-4529-9891-341e4f7cda30"
        run_id_2 = "e7b74cfc-2a67-463c-b30f-164ba258071d"
        
        b_resp = await client.get("http://localhost:8000/api/v1/businesses")
        businesses = b_resp.json()
        print(f"Total Businesses returned: {len(businesses)}")
        
        matching = []
        for b in businesses:
            d_resp = await client.get(f"http://localhost:8000/api/v1/businesses/{b['id']}")
            detail = d_resp.json()
            for sr in detail.get("source_records", []):
                if sr.get("target_run_id") in [run_id_1, run_id_2]:
                    matching.append(b)
                    break
        
        print(f"\nFound {len(matching)} businesses associated with target runs!")
        for m in matching:
            print(f" - {m['name']} | City: '{m['city']}' | Phone: {m['phone']} | Has Web: {m['has_website']}")

if __name__ == "__main__":
    asyncio.run(main())
