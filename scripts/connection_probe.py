import requests
import asyncio
import websockets

API_URL = "https://api.limitless.exchange/api-v1"

def test_rest():
    url = f"{API_URL}/markets"
    print(f"[LLMM] Testing REST: {url}")
    try:
        r = requests.get(url, timeout=5)
        print("[LLMM] Status:", r.status_code)
        print("[LLMM] Body sample:", r.text[:200], "...")
    except Exception as e:
        print("[LLMM] REST ERROR:", e)

async def test_ws():
    uri = API_URL.replace("https", "wss") + "/ws"
    print(f"[LLMM] Testing WS: {uri}")
    try:
        async with websockets.connect(uri, ping_interval=None) as ws:
            print("[LLMM] WS CONNECT OK")
    except Exception as e:
        print("[LLMM] WS ERROR:", e)

def main():
    print("[LLMM] Starting connection test...")
    test_rest()
    asyncio.run(test_ws())
    print("[LLMM] Connection test complete.")

if __name__ == "__main__":
    main()
