import os
import json
import asyncio
import requests
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL", "https://api.limitless.exchange")
MARKET_IDS = os.getenv("MARKET_IDS", "").split(",") if os.getenv("MARKET_IDS") else []

# --- REST hourly market data ---
def test_rest_hourly():
    url = f"{API_URL}/markets/hourly?limit=5"
    print(f"[LLMM] Testing REST hourly endpoint: {url}")
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            print("[LLMM] REST CONNECT OK")
            data = r.json()
            print("[LLMM] Latest hourly markets:")
            for m in data:
                print(f" - {m.get('title')} | Prices: {m.get('prices')} | Exp: {m.get('expirationDate')}")
        else:
            print(f"[LLMM] REST CONNECT FAIL (status {r.status_code})")
            print("Body:", r.text)
    except Exception as e:
        print(f"[LLMM] REST CONNECT ERROR: {e}")

# --- WebSocket hourly market data ---
async def test_ws_hourly():
    uri = API_URL.replace("https", "wss") + "/ws"
    print(f"[LLMM] Testing WS hourly endpoint: {uri}")
    try:
        async with websockets.connect(uri, ping_interval=None) as ws:
            print("[LLMM] WS CONNECT OK")
            if MARKET_IDS:
                # Subscribe to hourly market updates
                await ws.send(json.dumps({
                    "action": "subscribe",
                    "channel": "markets",
                    "ids": MARKET_IDS
                }))
                print(f"[LLMM] Subscribed to markets: {MARKET_IDS}")
                # Listen for a few events
                for _ in range(3):
                    msg = await ws.recv()
                    data = json.loads(msg)
                    print("[LLMM] WS EVENT:", data)
            else:
                print("[LLMM] No MARKET_IDS set in .env")
    except Exception as e:
        print(f"[LLMM] WS CONNECT ERROR: {e}")

def main():
    print("[LLMM] Starting market data test...")
    test_rest_hourly()
    asyncio.run(test_ws_hourly())
    print("[LLMM] Market data test complete.")

if __name__ == "__main__":
    main()
