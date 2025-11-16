#!/usr/bin/env python3
"""
Limitless Exchange Continuous Deep Category Scanner
Fetches category IDs + totals, then scans all markets within each category.
Displays ticker, strike, and deadline for operator clarity.
"""

import time
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def get_categories(session):
    """Fetch category IDs and counts."""
    url = f"{API_URL}/markets/categories/count"
    r = session.get(url, timeout=30)
    return r.json()

def get_markets_by_category(session, category_id, limit=100):
    """Fetch active markets for a given category ID."""
    url = f"{API_URL}/markets/active"
    params = {"category": category_id, "limit": str(limit)}
    r = session.get(url, params=params, timeout=30)
    # FIX: use 'markets' key instead of 'data'
    return r.json().get("markets", [])

def deep_scan(interval=180):
    """Scan category IDs, then deep scan all markets inside each category."""
    session = get_session()

    while True:
        data = get_categories(session)
        categories = data.get("category", {})
        total = data.get("totalCount", 0)

        print(f"\n[LLMM] Total active markets: {total}")
        for cat_id, count in categories.items():
            print(f"[LLMM] Category {cat_id} → {count} markets")

            markets = get_markets_by_category(session, cat_id)
            if not markets:
                print(f"  [LLMM] No markets found in category {cat_id}")
                continue

            for m in markets:
                ticker = m.get("ticker") or "N/A"
                strike = m.get("strikePrice") or "N/A"
                deadline = m.get("expirationDate") or "N/A"
                title = m.get("title") or m.get("slug")
                print(f"  - {title} | Ticker {ticker} | Strike {strike} | Deadline {deadline}")

        time.sleep(interval)

if __name__ == "__main__":
    deep_scan(interval=180)  # refresh every 3 minutes
