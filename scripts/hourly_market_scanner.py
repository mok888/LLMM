import json
import asyncio
import datetime
import requests
import websockets

GRAPHQL_URL = "https://api.limitless.exchange/graphql"
REST_URL = "https://api.limitless.exchange/api-v1"

def discover_hourly_market(limit=5):
    """Discover newest Hourly markets via GraphQL and return slug + id."""
    query = """
    {
      markets(page:1, limit:%d, sortBy:"newest", categories:["Hourly"]) {
        id
        slug
        title
        categories
      }
    }
    """ % limit

    print("[LLMM] Discovering Hourly markets via GraphQL...")
    try:
        r = requests.post(GRAPHQL_URL, json={"query": query}, timeout=15)
        r.raise_for_status()
        data = r.json()
        markets = data.get("data", {}).get("markets", [])
        if not markets:
            print("[LLMM] No Hourly markets found.")
            return None, None
        m = markets[0]
        print(f"[LLMM] Selected Hourly market slug={m['slug']} id={m['id']} title={m['title']}")
        return m["slug"], m["id"]
    except Exception as e:
        print("[LLMM] GraphQL discovery ERROR:", e)
        return None, None

def test_rest_hourly(slug, label):
    """Probe REST hourly endpoint for a given slug."""
    url = f"{REST_URL}/markets/{slug}/hourly"
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
    uri = f"{REST_URL}/ws".replace("https", "wss")
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
    slug, market_id = discover_hourly_market(limit=5)
    if slug and market_id:
        asyncio.run(hourly_scanner(slug, market_id))
    else:
        print("[LLMM] No Hourly market available to scan.")

if __name__ == "__main__":
    main()
