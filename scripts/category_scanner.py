#!/usr/bin/env python3
"""
Category-specific market fetcher
"""

import requests
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

CATEGORY_MAP = {
    "hourly": 29,
    "daily": 30,
    "weekly": 31,
    "30-min": 33,
    "crypto": 2,
    "economy": 23,
    "company-news": 19,
    "other": 5,
    "chinese": 39,
    "korean": 42,
    "billions-network-tge": 43,
}

def get_category_markets(session, category_name):
    cat_id = CATEGORY_MAP[category_name]
    url = f"{API_URL}/markets/active/{cat_id}"
    r = session.get(url, timeout=30)
    payload = r.json()
    return payload.get("markets", []) or payload.get("data", [])

if __name__ == "__main__":
    session = get_session()
    markets = get_category_markets(session, "billions-network-tge")
    print(f"[LLMM] Found {len(markets)} markets in Billions-Network-TGE")
    for m in markets:
        print(f"  + {m.get('title')} | Deadline {m.get('expirationDate')} | Volume {m.get('volumeFormatted')}")
