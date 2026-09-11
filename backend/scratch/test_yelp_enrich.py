import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json

async def enrich_yelp_biz(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
        res = await client.get(url, headers=headers)
        if res.status_code != 200:
            return None
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Phone extraction from page text or links
        phone = None
        phone_match = re.search(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", res.text)
        if phone_match:
            phone = phone_match.group(0)
            
        # Address extraction
        addr_match = re.search(r"(\d+\s+[A-Za-z0-9\s.]+,\s*New York,\s*NY\s*\d{5}?)", res.text)
        address = addr_match.group(1) if addr_match else None
        
        # Rating & Reviews
        rating_match = re.search(r"(\d\.\d)\s*\(\d+\s*reviews?\)", res.text)
        rating = float(rating_match.group(1)) if rating_match else None
        
        # Website redirect link on Yelp page
        website = None
        biz_website_link = soup.find("a", href=re.compile(r"/biz_redir\?"))
        if biz_website_link:
            raw_href = biz_website_link.get("href", "")
            import urllib.parse
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query)
            if "url" in parsed:
                website = parsed["url"][0]
                
        return {
            "phone": phone,
            "address": address,
            "rating": rating,
            "website": website,
        }

async def main():
    test_urls = [
        "https://www.yelp.com/biz/tribeca-dental-design-new-york",
        "https://www.yelp.com/biz/soho-dental-group-new-york-2",
        "https://www.yelp.com/biz/gramercy-park-dental-studio-new-york"
    ]
    for u in test_urls:
        data = await enrich_yelp_biz(u)
        print(f"URL: {u}")
        print(f"  Enriched: {data}\n")

if __name__ == "__main__":
    asyncio.run(main())
