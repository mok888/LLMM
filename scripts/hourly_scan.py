#!/usr/bin/env python3
"""
Hourly Market Scanner (Discovery)
Fetches active hourly markets and saves usable identifiers to hourly_markets.json
"""

import json
from limitless_auth import get_session

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

    # Extract usable identifiers
    addresses = []
    for m in hourly_markets:
        # Prefer conditionId if present
        if "conditionId" in m:
            addresses.append(m["conditionId"])
        # Fallback: yes/no token addresses
        elif "tokens" in m:
            addresses.extend([m["tokens"].get("yes"), m["tokens"].get("no")])

    print(f"[LLMM] Hourly markets discovered: {addresses}")

    with open("hourly_markets.json", "w") as f:
        json.dump(addresses, f, indent=2)
