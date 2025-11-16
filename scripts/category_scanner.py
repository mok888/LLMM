#!/usr/bin/env python3
"""
Limitless Exchange Category Markets Scanner
"""

import time
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def fetch_active_markets(session, page=1, limit=50):
    """Fetch active markets feed (no category param)."""
    url = f"{API_URL}/markets/active"
    params = {"page": str(page), "limit": str(limit), "sortBy": "newest"}
    r = session.get(url, params=params, timeout=30)
    if r.status_code != 200:
        print(f"[LLMM] Error fetching markets: {r.status_code}")
        return []
    try:
        return r.json().get("data", [])
    except Exception:
        print("[LLMM] Failed to parse JSON")
        return []

def scan_categories(session, categories, seen_ids):
    """Scan for markets in given categories and print new ones."""
    markets = fetch_active_markets(session)
    for cat in categories:
        filtered = [m for m in markets if any(c.lower() == cat.lower() for c in m.get("categories", []))]
        if not filtered:
            print(f"[LLMM] No {cat} markets found at this refresh.")
        for m in filtered:
            if m["id"] not in seen_ids:
                print(f"[LLMM] NEW {cat} Market → ID {m['id']} | {m['title']} | Status: {m['status']}")
                seen_ids.add(m["id"])

def main():
    session = get_session()
    seen_ids = set()
    categories = ["Daily", "Politics", "Crypto"]  # categories to scan
    print("[LLMM] Starting continuous category market scanner...")
    while True:
        scan_categories(session, categories, seen_ids)
        time.sleep(300)  # refresh every 5 minutes

if __name__ == "__main__":
    main()
