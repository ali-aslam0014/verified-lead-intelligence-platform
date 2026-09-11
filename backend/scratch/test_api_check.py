import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Trigger re-run on same target
        print("--- Triggering Re-Run ---")
        res = await client.post("http://localhost:8000/api/v1/targets/9b734f1a-4a45-46ee-aa21-c7864c61a944/runs")
        run_id = res.json()["id"]

        for i in range(10):
            await asyncio.sleep(1)
            p_res = await client.get(f"http://localhost:8000/api/v1/targets/9b734f1a-4a45-46ee-aa21-c7864c61a944/runs/{run_id}")
            data = p_res.json()
            print(f"Second {i+1}: Status={data['status']} | Discovered={data['total_discovered']} | Verified={data['total_verified']}")
            if data["status"] in ["COMPLETED", "FAILED"]:
                print("Re-Run Final Error Log:", data.get("error_log"))
                break

if __name__ == "__main__":
    asyncio.run(main())
