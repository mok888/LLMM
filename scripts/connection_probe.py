import requests
import asyncio
import websockets

REST_BASES = [
    "https://api.limitless.exchange/markets",
    "https://api.limitless.exchange/v1/markets"
]

WS_BASES = [
    "wss://api.limitless.exchange/ws",
    "wss://api.limitless.exchange/v1/ws",
    "wss://api.limitless.exchange/markets"
]

def probe_rest():
    print("[LLMM] Probing REST endpoints...")
    for url in REST_BASES:
        try:
            r = requests.get(url, timeout=5)
            print(f" -> {url} | status {r.status_code}")
            if r.status_code == 200:
                print("    Body sample:", r.text[:200], "...")
        except Exception as e:
            print(f"    ERROR: {e}")

async def probe_ws():
    print("[LLMM] Probing WS endpoints...")
    for uri in WS_BASES:
        try:
            async with websockets.connect(uri, ping_interval=None) as ws:
                print(f" -> {uri} | CONNECT OK")
        except Exception as e:
            print(f" -> {uri} | ERROR: {e}")

def main():
    print("[LLMM] Starting connection probe...")
    probe_rest()
    asyncio.run(probe_ws())
    print("[LLMM] Probe complete.")

if __name__ == "__main__":
    main()
