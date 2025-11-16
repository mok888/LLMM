#!/usr/bin/env python3
"""
Limitless Exchange Continuous Category Scanner (BTC/ETH filter)
Cycles through category IDs, fetches active markets, and prints lifecycle banners
only for BTC/ETH tickers.
"""

import time
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def get_categories(session):
    """Fetch category IDs and counts."""
    url = f"{API_URL}/markets/categories/count"
    r = session.get(url, timeout=30)
    return r.json()

def get_markets_by_category(session, category_id, limit=50):
    """Fetch active markets for a given category ID."""
    url = f"{API_URL}/markets/active"
    params = {"category": category_id, "limit": str(limit)}
    r = session.get(url, params=params, timeout=30)
    return r.json().get("data", [])

def continuous_scan(interval=120):
    """Continuously scan categories and filter BTC/ETH markets."""
    session = get_session()
    last_snapshot = {}

    while True:
        data = get_categories(session)
        categories = data.get("category", {})
        total = data.get("totalCount", 0)

        print(f"\n[LLMM] Total active markets: {total}")
        for cat_id, count in categories.items():
            markets = get_markets_by_category(session, cat_id)
            # Filter only BTC/ETH tickers
            btc_eth_markets = [m for m in markets if m.get("ticker") in ("BTC", "ETH")]
            current_ids = {m['id'] for m in btc_eth_markets}

            prev_ids = last_snapshot.get(cat_id, set())
            new_ids = current_ids - prev_ids
            removed_ids = prev_ids - current_ids

            if btc_eth_markets:
                print(f"[LLMM] Category {cat_id} → {len(btc_eth_markets)} BTC/ETH markets")

            if new_ids:
                print(f"[LLMM] NEW BTC/ETH markets in category {cat_id}:")
                for m in btc_eth_markets:
                    if m['id'] in new_ids:
                        print(f"  + {m['ticker']} | {m['title']} | Deadline {m['expirationDate']}")

            if removed_ids:
                print(f"[LLMM] REMOVED BTC/ETH markets in category {cat_id}:")
                for mid in removed_ids:
                    print(f"  - {mid}")

            # Update snapshot
            last_snapshot[cat_id] = current_ids

        time.sleep(interval)

if __name__ == "__main__":
    continuous_scan(interval=120)  # refresh every 2 minutes
