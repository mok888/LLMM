#!/usr/bin/env python3
"""
Limitless Exchange Continuous Category Scanner
- Fetches all active markets (paginated, limit=25, page=1,2,...)
- Filters locally by category labels (e.g. "Weekly", "Economy")
- Prints lifecycle banners for operator clarity
"""

import time
from typing import Dict
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

# Map operator-friendly labels to backend category strings
CATEGORY_MAP: Dict[str, str] = {
    "hourly": "Hourly",
    "daily": "Daily",
    "weekly": "Weekly",
    "30-min": "30-min",
    "crypto": "Crypto",
    "economy": "Economy",
    "company-news": "Company-News",
    "other": "Other",
    "chinese": "Chinese",
    "korean": "Korean",
    "billions-network-tge": "Billions-Network-TGE",
}

def get_active_markets(session, limit=25, page=1):
    """Fetch active markets with pagination (limit <= 25, page-based)."""
    url = f"{API_URL}/markets/active"
    params = {"limit": str(limit), "page": str(page)}
    r = session.get(url, params=params, timeout=30)
    payload = r.json()
    return payload.get("markets", []) or payload.get("data", [])

def fetch_all_active(session):
    """Fetch all active markets by paginating until exhausted."""
    all_markets = []
    page = 1
    batch_size = 25

    while True:
        markets = get_active_markets(session, limit=batch_size, page=page)
        if not markets:
            break
        all_markets.extend(markets)
        print(f"[LLMM] Captured page {page}: {len(markets)} markets")
        page += 1
        if len(markets) < batch_size:
            break

    return all_markets

def continuous_scan(interval=180):
    """Continuously fetch all active markets and filter by category labels."""
    session = get_session()
    last_snapshot = {}

    while True:
        all_markets = fetch_all_active(session)
        print(f"\n[LLMM] Total active markets: {len(all_markets)}")

        for label, category in CATEGORY_MAP.items():
            filtered = [m for m in all_markets if category in m.get("categories", [])]
            current_ids = {m['id'] for m in filtered}
            prev_ids = last_snapshot.get(category, set())

            new_ids = current_ids - prev_ids
            removed_ids = prev_ids - current_ids

            print(f"[LLMM] Category {category} ({label}) → {len(filtered)} markets")

            if new_ids:
                print(f"  [LLMM] NEW markets in {label}:")
                for m in filtered:
                    if m['id'] in new_ids:
                        print(f"    + {m['title']} | {m['ticker']} | Deadline {m['expirationDate']}")

            if removed_ids:
                print(f"  [LLMM] REMOVED markets in {label}:")
                for mid in removed_ids:
                    print(f"    - {mid}")

            last_snapshot[category] = current_ids

        time.sleep(interval)

if __name__ == "__main__":
    continuous_scan(interval=180)  # refresh every 3 minutes
