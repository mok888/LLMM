import os
import json
import asyncio
import requests
import websockets

API_URL = "https://api.limitless.exchange/api-v1"

# --- CONFIG: set a real slug here ---
# Replace with a valid slug from Limitless UI/docs
SLUG = "president-2024-1731715200"

def test_rest():
    url = f"{API_URL}/markets/{SLUG}/hourly"
    print(f"[LLMM] Testing REST hourly: {url}")
    try:
        r = requests.get(url, timeout=5)
        print("[LLMM] Status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            print("[LLMM] REST HOURLY OK")
            print(json.dumps(data, indent=2)[:500], "...")
            # Extract marketId if present
            market_id = data.get("id") or data.get("marketId")
            return market_id
        else:
            print("[LLMM] REST HOURLY FAIL")
            print("Body sample:", r.text[:200], "...")
            return None
    except Exception as e:
        print("[LLMM] REST ERROR:", e)
        return None

async def test_ws(market_id):
    uri = API_URL.replace("https", "wss") + "/ws"
    print(f"[LLMM] Testing WS: {uri}")
    try:
        async with websockets.connect(uri, ping_interval=None) as ws:
            print("[LLMM] WS CONNECT OK")
            if market_id:
                sub = {
                    "action": "subscribe",
                    "channel": "markets",
                    "ids": [market_id]
                }
                await ws.send(json.dumps(sub))
                print(f"[LLMM] Subscribed to market id={market_id}")
                for _ in range(3):
                    msg = await ws.recv()
                    print("[LLMM] WS EVENT:", msg)
            else:
                print("[LLMM] No market id provided.")
    except Exception as e:
        print("[LLMM] WS ERROR:", e)

def main():
    print("[LLMM] Starting real market data test...")
    market_id = test_rest()
    asyncio.run(test_ws(market_id))
    print("[LLMM] Market data test complete.")

if __name__ == "__main__":
    main()
