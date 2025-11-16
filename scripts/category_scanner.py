#!/usr/bin/env python3
"""
Limitless Exchange Slugs Test
Fetches active market slugs with metadata for specific tickers (e.g. BTC, ETH).
"""

import json
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def get_slugs(session, tickers):
    """Fetch slugs for given tickers."""
    url = f"{API_URL}/markets/active/slugs"
    params = {"tickers": ",".join(tickers)}  # e.g. "btc,eth"
    r = session.get(url, params=params, timeout=30)
    print("[LLMM] Slugs status:", r.status_code)
    try:
        data = r.json()
        print(json.dumps(data, indent=2)[:2000])  # preview first 2000 chars
        return data
    except ValueError:
        print("[LLMM] Raw response:", r.text)
        return {}

def main():
    session = get_session()
    # Test with BTC and ETH
    get_slugs(session, ["btc", "eth"])

if __name__ == "__main__":
    main()
