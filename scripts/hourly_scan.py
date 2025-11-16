#!/usr/bin/env python3
"""
Hourly Market Scanner (Discovery)
Fetches active hourly markets and saves their addresses to hourly_markets.json
"""

import json
import requests
from limitless_auth import get_session  # your existing auth helper

API_URL = "https://api.limitless.exchange"

def get_hourly_markets(session):
    url = f"{API_URL}/markets/active/29"  # categoryId for hourly
    r = session.get(url, timeout=30)
    r.raise_for_status()
    payload = r.json()
    return payload.get("markets", []) or payload.get("data", [])

if __name__ == "__main__":
    session = get_session()
    hourly_markets = get_hourly_markets(session)

    # Extract market addresses (not IDs)
    addresses = []
    for m in hourly_markets:
        addr = m.get("marketAddress")
        if addr:
            addresses.append(addr)

    print(f"[LLMM] Hourly markets discovered: {addresses}")

    # Save addresses to file for cockpit to consume
    with open("hourly_markets.json", "w") as f:
        json.dump(addresses, f, indent=2)
