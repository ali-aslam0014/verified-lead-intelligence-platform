import asyncio
import httpx

async def main():
    target_id = "f8ced3c2-4afc-47a2-a395-ef8aafd3ebf2"
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(f"http://localhost:8000/api/v1/businesses?target_id={target_id}")
        data = res.json()
        print(f"Target ID: {target_id}")
        print(f"Total Discovered Leads Returned for Target: {len(data)}")
        for item in data:
            print(f" - {item['name']} | City: {item['city']} | Phone: {item['phone']} | Has Web: {item['has_website']}")

if __name__ == "__main__":
    asyncio.run(main())
