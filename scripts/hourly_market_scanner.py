import json
import asyncio
import datetime
import requests
import websockets

API_URL = "https://api.limitless.exchange"

def discover_hourly_market(page=1, limit=10):
    """Discover newest Hourly market and return slug + id."""
    url = f"{API_URL}/markets/active/{page}"
    params = {"page": str(page), "limit": str(limit), "sortBy": "newest"}
    print(f"[LLMM] Discovering Hourly markets: {url} {params}")
    r = requests.get(url, params=params, timeout=5)
    data = r.json()
    markets = data.get("data", [])
    hourly_markets = [m for m in markets if "Hourly" in m.get("categories", [])]
    if not hourly_markets:
        print("[LLMM] No Hourly markets found.")
        return None, None
    m = hourly_markets[0]
    print(f"[LLMM] Selected Hourly market slug={m['slug']} id={m['id']} title={m['title']}")
    return m["slug"], m["id"]

def test_rest_hourly(slug, label):
    """Probe REST hourly endpoint for a given slug."""
    url = f"{API_URL}/api-v1/markets/{slug}/hourly"
    print(f"[LLMM] {label} REST hourly probe: {url}")
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
            for _ in range(5):  # print 5 events after rollover
                msg = await ws.recv()
                print("[LLMM] WS EVENT:", msg)
    except Exception as e:
        print("[LLMM] WS ERROR:", e)

async def hourly_scanner(slug, market_id):
    """Run probes at HH:59:55 and HH:00:15 for one market."""
    while True:
        now = datetime.datetime.now()
        next_hour = (now.replace(minute=0, second=0, microsecond=0)
                     + datetime.timedelta(hours=1))
        before = next_hour - datetime.timedelta(seconds=5)
        after = next_hour + datetime.timedelta(seconds=15)

        # Sleep until 59:55
        await asyncio.sleep((before - datetime.datetime.now()).total_seconds())
        test_rest_hourly(slug, "PREVIOUS HOUR END")

        # Sleep until 00:15
        await asyncio.sleep((after - datetime.datetime.now()).total_seconds())
        test_rest_hourly(slug, "NEXT HOUR START")
        await test_ws(market_id)

def main():
    print("[LLMM] Starting Hourly market scanner...")
    slug, market_id = discover_hourly_market(limit=10)
    if slug and market_id:
        asyncio.run(hourly_scanner(slug, market_id))
    else:
        print("[LLMM] No Hourly market available to scan.")

if __name__ == "__main__":
    main()
