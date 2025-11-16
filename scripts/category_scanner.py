#!/usr/bin/env python3
"""
Limitless Exchange Continuous Category Scanner
- Fetches all active markets (paginated, limit=25)
- Filters locally by categoryId using CATEGORY_MAP
- Prints lifecycle banners for operator clarity
"""

import time
from typing import Dict
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

CATEGORY_MAP: Dict[str, int] = {
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

def get_active_markets(session, limit=25, offset=0):
    """Fetch active markets with pagination (limit <= 25)."""
    url = f"{API_URL}/markets/active"
    params = {"limit": str(limit), "offset": str(offset)}
    r = session.get(url, params=params, timeout=30)
    payload = r.json()
    return payload.get("markets", []) or payload.get("data", [])

def fetch_all_active(session):
    """Fetch all active markets by paginating until exhausted."""
    all_markets = []
    offset = 0
    batch_size = 25

    while True:
        markets = get_active_markets(session, limit=batch_size, offset=offset)
        if not markets:
            break
        all_markets.extend(markets)
        offset += batch_size
        if len(markets) < batch_size:
            break

    return all_markets

def continuous_scan(interval=180):
    """Continuously fetch all active markets and filter by category."""
    session = get_session()
    last_snapshot = {}

    while True:
        all_markets = fetch_all_active(session)
        print(f"\n[LLMM] Total active markets: {len(all_markets)}")

        for label, cat_id in CATEGORY_MAP.items():
            filtered = [m for m in all_markets if str(m.get("categoryId")) == str(cat_id)]
            current_ids = {m['id'] for m in filtered}
            prev_ids = last_snapshot.get(cat_id, set())

            new_ids = current_ids - prev_ids
            removed_ids = prev_ids - current_ids

            print(f"[LLMM] Category {cat_id} ({label}) → {len(filtered)} markets")

            if new_ids:
                print(f"  [LLMM] NEW markets in {label}:")
                for m in filtered:
                    if m['id'] in new_ids:
                        print(f"    + {m['title']} | {m['ticker']} | Deadline {m['expirationDate']}")

            if removed_ids:
                print(f"  [LLMM] REMOVED markets in {label}:")
                for mid in removed_ids:
                    print(f"    - {mid}")

            last_snapshot[cat_id] = current_ids

        time.sleep(interval)

if __name__ == "__main__":
    continuous_scan(interval=180)  # refresh every 3 minutes
