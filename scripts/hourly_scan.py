#!/usr/bin/env python3
"""
Hourly Market Scanner with Debug
- Fetches active hourly markets
- Saves {conditionId: title} mapping
- Prints raw payload samples for operator clarity
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

    # Build mapping {conditionId: title}
    market_map = {}
    for m in hourly_markets:
        cid = m.get("conditionId")
        title = m.get("title")
        if cid and title:
            market_map[cid] = title

    print(f"[LLMM] Hourly markets discovered: {len(market_map)}")

    if hourly_markets:
        print("   Raw payload sample:")
        print(json.dumps(hourly_markets[:2], indent=2))  # show first 2 markets

    for cid, title in market_map.items():
        print(f"   {cid[:6]}… → {title}")

    # Save mapping to file
    with open("hourly_markets.json", "w") as f:
        json.dump(market_map, f, indent=2)
    print("[LLMM] Saved hourly_markets.json")