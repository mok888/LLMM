import os
import json
import asyncio
import requests
import websockets

API_URL = "https://api.limitless.exchange/api-v1"

# --- CONFIG: use the real slug from your example ---
SLUG = "us-stagflation-in-2025-1744723334416"

def get_market_details(slug):
    url = f"{API_URL}/markets/{slug}"
    print(f"[LLMM] Fetching market details: {url}")
    try:
        r = requests.get(url, timeout=5)
        print("[LLMM] Status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            print("[LLMM] Market details OK")
            print(json.dumps(data, indent=2)[:500], "...")
            market_id = data.get("id")
            return market_id
        else:
            print("[LLMM] Market details FAIL")
            print("Body sample:", r.text[:200], "...")
            return None
    except Exception as e:
        print("[LLMM] REST ERROR:", e)
        return None

def test_rest_hourly(slug):
    url = f"{API_URL}/markets/{slug}/hourly"
    print(f"[LLMM] Testing REST hourly: {url}")
    try:
        r = requests.get(url, timeout=5)
        print("[LLMM] Status:", r.status_code)
        if r.status_code == 200:
            try:
                data = r.json()
                print("[LLMM] REST HOURLY OK")
                print(json.dumps(data, indent=2)[:500], "...")
            except Exception:
                print("[LLMM] Response not JSON, body sample:", r.text[:200], "...")
        else:
            print("[LLMM] REST HOURLY FAIL")
            print("Body sample:", r.text[:200], "...")
    except Exception as e:
        print("[LLMM] REST ERROR:", e)

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
    market_id = get_market_details(SLUG)
    test_rest_hourly(SLUG)
    asyncio.run(test_ws(market_id))
    print("[LLMM] Market data test complete.")

if __name__ == "__main__":
    main()
