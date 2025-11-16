#!/usr/bin/env python3
"""
Limitless Exchange Active Market Slugs Scanner
Retrieves slugs, strike prices, tickers, and deadlines for all active markets.
"""

import json
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def get_active_slugs(session):
    """Fetch active market slugs with metadata."""
    url = f"{API_URL}/markets/active/slugs"
    r = session.get(url, timeout=30)
    print("[LLMM] Slugs status:", r.status_code)
    try:
        data = r.json()
        print("[LLMM] Active market slugs with metadata:")
        # Preview first few entries
        for group in data.get("groups", []):
            print(f"Group: {group['name']}")
            for m in group.get("markets", []):
                print(f"  - Slug: {m['slug']} | Ticker: {m['ticker']} | Strike: {m['strikePrice']} | Deadline: {m['deadline']}")
        return data
    except ValueError:
        print("[LLMM] Raw response:", r.text)
        return {}

def main():
    session = get_session()
    get_active_slugs(session)

if __name__ == "__main__":
    main()
