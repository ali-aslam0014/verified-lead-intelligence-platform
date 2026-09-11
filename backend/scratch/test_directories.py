import asyncio
import httpx
from bs4 import BeautifulSoup
import urllib.parse

async def test_yelp_scrape():
    niche = "dentist"
    geo = "New York, NY"
    url = f"https://www.yelp.com/search?find_desc={urllib.parse.quote(niche)}&find_loc={urllib.parse.quote(geo)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    print(f"Fetching Yelp URL: {url}")
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        res = await client.get(url, headers=headers)
        print(f"Yelp Status Code: {res.status_code}")
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # Find business containers or links
            links = soup.find_all("a", href=True)
            biz_links = [l for l in links if "/biz/" in l.get("href", "")]
            print(f"Found {len(biz_links)} Yelp biz links!")
            for l in biz_links[:10]:
                print(f"  Name: {l.get_text(strip=True)} -> {l.get('href')}")

async def test_yellowpages_scrape():
    niche = "dentist"
    geo = "New York, NY"
    url = f"https://www.yellowpages.com/search?search_terms={urllib.parse.quote(niche)}&geo_location_terms={urllib.parse.quote(geo)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    print(f"\nFetching YellowPages URL: {url}")
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        res = await client.get(url, headers=headers)
        print(f"YP Status Code: {res.status_code}")
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.find_all("div", class_="result")
            print(f"Found {len(cards)} YellowPages business cards!")
            for card in cards[:10]:
                name_el = card.find("a", class_="business-name")
                phone_el = card.find("div", class_="phones")
                street_el = card.find("div", class_="street-address")
                locality_el = card.find("div", class_="locality")
                website_el = card.find("a", class_="track-visit-website")
                
                name = name_el.get_text(strip=True) if name_el else None
                phone = phone_el.get_text(strip=True) if phone_el else None
                street = street_el.get_text(strip=True) if street_el else ""
                locality = locality_el.get_text(strip=True) if locality_el else ""
                website = website_el.get("href") if website_el else None
                print(f"  Biz: {name} | Phone: {phone} | Address: {street}, {locality} | Website: {website}")

if __name__ == "__main__":
    asyncio.run(test_yelp_scrape())
    asyncio.run(test_yellowpages_scrape())
