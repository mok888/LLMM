import json
import asyncio
import datetime
import requests
import websockets
import time

API_URL = "https://api.limitless.exchange"

def discover_hourly_market(page=1, limit=10, retries=3):
    """Discover newest Hourly market via REST /markets/active."""
    url = f"{API_URL}/markets/active"
    params = {"page": str(page), "limit": str(limit), "sortBy": "newest"}
    print(f"[LLMM] Discovering Hourly markets: {url} {params}")
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                data = r.json()
                markets = data.get("data", [])
                hourly_markets = [m for m in markets if "Hourly" in m.get("categories", [])]
                if not hourly_markets:
                    print("[LLMM] No Hourly markets found.")
                    return None, None
                m = hourly_markets[0]
                print(f"[LLMM] Selected Hourly market slug={m['slug']} id={m['id']} title={m['title']}")
                return m["slug"], m["id"]
            else:
                print(f"[LLMM] Discovery failed: {r.status_code} {r.text}")
        except requests.exceptions.ReadTimeout:
            wait = 2 ** attempt
            print(f"[LLMM] Timeout on attempt {attempt+1}, retrying in {wait}s...")
            time.sleep(wait)
        except Exception as e:
            print("[LLMM] Discovery ERROR:", e)
            time.sleep(2)
    return None, None

def test_rest_hourly(slug, label):
    """Probe REST hourly endpoint for a given slug."""
    url = f"{API_URL}/api-v1/markets/{slug}/hourly"
    print(f"[LLMM] {label} REST hourly probe: {url}")
    try:
        r = requests.get(url, timeout=15)
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
    """Subscribe to WS feed for a given market id."""
    uri = f"{API_URL}/api-v1/ws".replace("https", "wss")
    print(f"[LLMM] Testing WS: {uri}")
    try:
        async with websockets.connect(uri, ping_interval=None) as ws:
            print("[LLMM] WS CONNECT OK")
            sub = {
                "action": "subscribe",
                "channel": "markets",
                "ids": [market_id]
            }
            await ws.send(json.dumps(sub))
            print(f"[LLMM] Subscribed to market id={market_id}")
            for _ in range(5):
                msg = await ws.recv()
                print("[LLMM] WS