import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json

async def test_yelp_detail():
    url = "https://www.yelp.com/biz/tribeca-dental-design-new-york"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    print(f"Fetching Yelp Biz Detail: {url}")
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        res = await client.get(url, headers=headers)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Find JSON-LD script tag
            scripts = soup.find_all("script", type="application/ld+json")
            for s in scripts:
                try:
                    data = json.loads(s.string)
                    if isinstance(data, dict) and data.get("@type") in ["LocalBusiness", "Dentist", "Physician", "LegalService", "PlumbingService", "ProfessionalService"]:
                        print("\n--- JSON-LD Data Extracted from Yelp ---")
                        print(f"Name: {data.get('name')}")
                        print(f"Telephone: {data.get('telephone')}")
                        print(f"Address: {data.get('address')}")
                        print(f"WebsiteUri: {data.get('url')}")
                        print(f"AggregateRating: {data.get('aggregateRating')}")
                        return
                except Exception:
                    pass
            print("No JSON-LD found, printing snippet text...")
            print(soup.get_text()[:500])

if __name__ == "__main__":
    asyncio.run(test_yelp_detail())
