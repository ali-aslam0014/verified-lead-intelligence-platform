import asyncio
import httpx
from bs4 import BeautifulSoup
import urllib.parse
import re
import hashlib

async def parse_yelp_search(niche: str, geography: str):
    query_loc = urllib.parse.quote(geography)
    query_desc = urllib.parse.quote(niche)
    url = f"https://www.yelp.com/search?find_desc={query_desc}&find_loc={query_loc}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    print(f"Fetching Yelp: {url}")
    results = []
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        res = await client.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Yelp HTTP Error: {res.status_code}")
            return results
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Yelp biz links on search result page
        links = soup.find_all("a", href=True)
        seen_names = set()
        
        for l in links:
            href = l.get("href", "")
            if "/biz/" in href and not href.startswith("/biz_attribute") and not "hrid=" in href:
                name = l.get_text(strip=True)
                if not name or name.lower() in ["more", "write a review", "claim", "read more"]:
                    continue
                if name in seen_names:
                    continue
                seen_names.add(name)
                
                # Try to find nearby parent elements for phone, rating, address
                parent = l.find_parent("div")
                text_block = parent.get_text(" ", strip=True) if parent else ""
                
                # Extract rating if present
                rating_match = re.search(r"(\d\.\d)\s*\(\d+\s*reviews?\)", text_block)
                rating = float(rating_match.group(1)) if rating_match else None
                
                # Extract review count
                review_match = re.search(r"\((\d+)\s*reviews?\)", text_block)
                review_count = int(review_match.group(1)) if review_match else 0
                
                biz_payload = {
                    "name": name,
                    "address": f"{geography}",
                    "phone": None,  # Will be enriched or extracted strictly
                    "website": None,  # STRICT: NONE unless verified
                    "has_website": False,
                    "rating": rating,
                    "review_count": review_count,
                    "social_links": {},  # STRICT: EMPTY dict unless found
                    "provider_source": "yelp_direct_directory",
                    "yelp_url": f"https://www.yelp.com{href.split('?')[0]}",
                }
                results.append(biz_payload)
                
    print(f"Extracted {len(results)} real Yelp businesses for '{niche} in {geography}':")
    for b in results[:10]:
        print(f"  - {b['name']} | Rating: {b['rating']} ({b['review_count']} reviews) | Website: {b['website']} | URL: {b['yelp_url']}")
        
    return results

if __name__ == "__main__":
    asyncio.run(parse_yelp_search("dentist", "New York, NY"))
