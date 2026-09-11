import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json

async def test_yelp_search_json():
    url = "https://www.yelp.com/search?find_desc=dentist&find_loc=New+York%2C+NY"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    print(f"Fetching Yelp Search: {url}")
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        res = await client.get(url, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            scripts = soup.find_all("script")
            for s in scripts:
                txt = s.string or ""
                if "searchResultProps" in txt or "organicSearchResultLayout" in txt:
                    print("Found search results script JSON snippet!")
                    print(txt[:1000])
                    break
            
            # Let's inspect biz cards
            biz_cards = soup.find_all("div", class_=re.compile(r"container__"))
            print(f"Found {len(biz_cards)} container divs.")

if __name__ == "__main__":
    asyncio.run(test_yelp_search_json())
