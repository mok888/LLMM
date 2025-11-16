#!/usr/bin/env python3
"""
Test run: Capture active markets from one category (e.g. crypto).
"""

from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

CATEGORY_MAP = {
    "crypto": 2,
    "economy": 23,
    "company-news": 19,
    "other": 5,
    "hourly": 29,
    "daily": 30,
    "weekly": 31,
    "30-min": 33,
    "chinese": 39,
    "korean": 42,
    "billions-network-tge": 43,
}

def get_active_markets(session, category_id, limit=25, offset=0):
    """Fetch active markets for a given category ID with pagination."""
    url = f"{API_URL}/markets/active"
    params = {"limit": str(limit), "offset": str(offset), "categorySlug": "crypto"}
    # NOTE: using categorySlug instead of categoryId, since backend rejects categoryId
    r = session.get(url, params=params, timeout=30)
    payload = r.json()
    return payload.get("markets", []) or payload.get("data", [])

def test_category(category_label="crypto", max_markets=50):
    session = get_session()
    category_id = CATEGORY_MAP.get(category_label)
    print(f"[LLMM] Testing category '{category_label}' (ID={category_id})")

    all_markets = []
    offset = 0
    batch_size = 25

    while len(all_markets) < max_markets:
        markets = get_active_markets(session, category_id, limit=batch_size, offset=offset)
        if not markets:
            break
        all_markets.extend(markets)
        print(f"[LLMM] Captured {len(markets)} markets from {category_label} (offset={offset})")
        offset += batch_size
        if len(markets) < batch_size:
            break

    print(f"\n[LLMM] Total captured {category_label} markets: {len(all_markets)}")
    for m in all_markets:
        ticker = m.get("ticker") or "N/A"
        title = m.get("title") or m.get("slug")
        deadline = m.get("expirationDate") or "N/A"
        print(f"- {title} | Ticker {ticker} | Deadline {deadline}")

if __name__ == "__main__":
    test_category("crypto", max_markets=50)
