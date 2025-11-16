#!/usr/bin/env python3
"""
Debug Scanner
Sweeps categories, prints raw payloads, and extracts market addresses if present
"""

import json
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

CATEGORY_MAP = {
    "hourly": 29,
    "daily": 30,
    "weekly": 31,
    "tge": 43
}

def get_markets(session, category_id):
    url = f"{API_URL}/markets/active/{category_id}"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    payload = r.json()
    return payload.get("markets", []) or payload.get("data", [])

if __name__ == "__main__":
    session = get_session()

    for name, cid in CATEGORY_MAP.items():
        markets = get_markets(session, cid)
        print(f"\n[LLMM] Category {name} ({cid}) → {len(markets)} markets")

        if not markets:
            print("   ⚠️ No markets returned")
            continue

        # Print raw payload for operator clarity
        print("   Raw payload sample:")
        print(json.dumps(markets[:2], indent=2))  # show first 2

        # Extract addresses if present
        addresses = [m.get("marketAddress") for m in markets if "marketAddress" in m]
        if addresses:
            print(f"   ✅ Extracted {len(addresses)} market addresses: {addresses}")
        else:
            print("   ⚠️ No 'marketAddress' field found, check payload keys")
