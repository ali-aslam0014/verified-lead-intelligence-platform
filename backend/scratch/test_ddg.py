import asyncio
import httpx
import time

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
            resp = await client.get("https://html.duckduckgo.com/html/?q=Plumber+in+New+York+NY", headers=headers)
            print("GET Status:", resp.status_code, "Time:", round(time.time() - t0, 2))
    except Exception as e:
        print("GET Error:", e, "Time:", round(time.time() - t0, 2))

if __name__ == "__main__":
    asyncio.run(main())
