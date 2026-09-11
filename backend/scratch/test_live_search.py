import asyncio
import httpx
from bs4 import BeautifulSoup
import urllib.parse

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    url = "https://www.google.com/search?q=Plumber+in+New+York+NY"
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        print("Google Status:", resp.status_code)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Google Business Cards / Maps entries or organic titles
            headings = soup.find_all(["h3", "div"], class_=lambda c: c and ("r" in c or "vv4w3b" in c or "Vkpbdw" in c))
            print(f"Google headings found: {len(headings)}")
            for h in soup.find_all("h3")[:10]:
                print(" - H3:", h.get_text(strip=True))

if __name__ == "__main__":
    asyncio.run(main())
