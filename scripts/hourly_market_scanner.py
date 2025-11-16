import json
import asyncio
import datetime
import requests
import websockets
import argparse

API_URL = "https://api.limitless.exchange"

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
                print("[LLMM] WS EVENT:", msg)
    except Exception as e:
        print("[LLMM] WS ERROR:", e)

async def hourly_scanner(slug, market_id, fast_forward=False):
    """Run probes at HH:59:55 and HH:00:15 (or fast-forward for testing)."""
    while True:
        if fast_forward:
            before = datetime.datetime.now() + datetime.timedelta(seconds=10)
            after = datetime.datetime.now() + datetime.timedelta(seconds=20)
        else:
            now = datetime.datetime.now()
            next_hour = (now.replace(minute=0, second=0, microsecond=0)
                         + datetime.timedelta(hours=1))
            before = next_hour - datetime.timedelta(seconds=5)
            after = next_hour + datetime.timedelta(seconds=15)

        await asyncio.sleep((before - datetime.datetime.now()).total_seconds())
        test_rest_hourly(slug, "PREVIOUS HOUR END")

        await asyncio.sleep((after - datetime.datetime.now()).total_seconds())
        test_rest_hourly(slug, "NEXT HOUR START")
        await test_ws(market_id)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run in fast-forward mode")
    args = parser.parse_args()

    print("[LLMM] Starting Hourly market scanner...")

    # 🔧 Directly specify a known active market
    slug = "dollardoge-above-dollar021652-on-sep-1-1200-utc-1756724413009"
    market_id = 7495

    if slug and market_id:
        asyncio.run(hourly_scanner(slug, market_id, fast_forward=args.test))
    else:
        print("[LLMM] No Hourly market available to scan.")

if __name__ == "__main__":
    main()
