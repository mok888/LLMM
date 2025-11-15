import os
import json
import asyncio
import requests
import websockets

API_URL = "https://api.limitless.exchange/api-v1"

# --- REST: discover markets and fetch hourly data ---
def discover_market():
    url = f"{API_URL}/markets?limit=5"
    print(f"[LLMM] Discovering markets from: {url}")
    try:
        r = requests.get(url, timeout=5)
        print("[LLMM] Status:", r.status_code)
        if r.status_code != 200:
            print("Body sample:", r.text[:200], "...")
            return None, None

        markets = r.json()
        if not markets or not isinstance(markets, list):
            print("[LLMM] No markets returned or invalid format.")
            return None, None

        first = markets[0]
        slug = first.get("slug")
        market_id = first.get("id")
        print(f"[LLMM] Discovered slug={slug}, id={market_id}")
        return slug, market_id
    except Exception as e:
        print("[LLMM] REST ERROR:", e)
        return None, None

def test_rest_hourly(slug):
    if not slug:
        return
    url = f"{API_URL}/markets/{slug}/hourly"
    print(f"[LLMM] Testing REST hourly: {url}")
    try:
        r = requests.get(url, timeout=5)
        print("[LLMM] Status:", r.status_code)
        if r.status_code == 200:
            print("[LLMM] REST HOURLY OK")
            print(json.dumps(r.json(), indent=2)[:500], "...")
        else:
            print("[LLMM] REST HOURLY FAIL")
            print("Body sample:", r.text[:200], "...")
    except Exception as e:
        print("[LLMM] REST ERROR:", e)

# --- WebSocket: subscribe to market events ---
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
    print("[LLMM] Starting market data test...")
    slug, market_id = discover_market()
    test_rest_hourly(slug)
    asyncio.run(test_ws(market_id))
    print("[LLMM] Market data test complete.")

if __name__ == "__main__":
    main()
