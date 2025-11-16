#!/usr/bin/env python3
"""
Limitless Exchange Hourly Markets Continuous Scanner
"""

import time
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def fetch_active_markets(session, page=1, limit=50):
    """Fetch active markets feed."""
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

def scan_hourly(session, seen_ids):
    """Scan for Hourly markets and print new ones."""
    markets = fetch_active_markets(session)
    hourly = [m for m in markets if "Hourly" in m.get("categories", [])]
    for m in hourly:
        if m["id"] not in seen_ids:
            print(f"[LLMM] NEW Hourly Market → ID {m['id']} | {m['title']} | Status: {m['status']}")
            seen_ids.add(m["id"])
    if not hourly:
        print("[LLMM] No Hourly markets found at this refresh.")

def main():
    session = get_session()
    seen_ids = set()
    print("[LLMM] Starting continuous Hourly market scanner...")
    while True:
        scan_hourly(session, seen_ids)
        time.sleep(300)  # refresh every 5 minutes

if __name__ == "__main__":
    main()
