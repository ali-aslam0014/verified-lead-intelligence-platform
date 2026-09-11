import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Get all targets to find "Law Firm in New York"
        t_resp = await client.get("http://localhost:8000/api/v1/targets")
        targets = t_resp.json()
        print("--- Targets ---")
        law_target = None
        for t in targets:
            print(f"Target ID: {t['id']} | Name: {t['name']} | Niche: {t['niche']} | Geo: {t['geography']}")
            if "law" in t["niche"].lower() or "law" in t["name"].lower():
                law_target = t

        # Get all businesses
        b_resp = await client.get("http://localhost:8000/api/v1/businesses")
        businesses = b_resp.json()
        print(f"\n--- Total Businesses in DB: {len(businesses)} ---")
        for b in businesses[:10]:
            print(f" - ID: {b['id']} | Name: {b['name']} | Category: {b['category']} | City: {b['city']} | Address: {b['address']}")

        # Test searching with search="Law Firm" and city="New York"
        search_resp = await client.get("http://localhost:8000/api/v1/businesses?search=Law%20Firm&city=New%20York")
        print("\n--- Backend Filter Search Result for search='Law Firm'&city='New York' ---")
        print(search_resp.json())

if __name__ == "__main__":
    asyncio.run(main())
