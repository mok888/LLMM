import os
import json
import asyncio
import requests
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL", "https://api.limitless.exchange/v1")

# --- REST: discover markets and fetch hourly data ---
def test_rest_hourly():
    try:
        # Step 1: list markets
        list_url = f"{API_URL}/markets"
        print(f"[LLMM] Fetching markets from: {list_url}")
        r = requests.get(list_url, timeout=5)
        if r.status_code != 200:
            print(f"[LLMM] REST FAIL (status {r.status_code})")
            print("Body:", r.text)
            return None, None

        markets = r.json()
        if not markets:
            print("[LLMM] No markets returned.")
            return None, None

        # Pick first market
        slug = markets[0]["slug"]
        market_id = markets[0]["id"]
        print(f"[LLMM] Using market slug={slug}, id={market_id}")

        # Step 2: fetch hourly data for that slug
        hourly_url = f"{API_URL}/markets/{slug}/hourly"
        print(f"[LLMM] Fetching hourly data from: {hourly_url}")
        hr = requests.get(hourly_url, timeout=5)
        if hr.status_code == 200:
            print("[LLMM] REST HOURLY OK")
            print(json.dumps(hr.json(), indent=2))
        else:
            print(f"[LLMM] REST HOURLY FAIL (status {hr.status_code})")
            print("Body:", hr.text)

        return slug, market_id
    except Exception as e:
        print(f"[LLMM] REST ERROR: {e}")
        return