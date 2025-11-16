#!/usr/bin/env python3
"""
Limitless Exchange Hourly Markets Scanner
Uses the stable authentication from limitless_auth.py
"""

import json
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def list_hourly_markets(session, page=1, limit=20):
    """Fetch active hourly markets."""
    url = f"{API_URL}/markets/active"
    params = {
        "page": page,
        "limit": limit,
        "sortBy": "newest",
        "categories": "Hourly"   # filter for hourly markets
    }
    r = session.get(url, params=params, timeout=30)
    print("[LLMM] Hourly markets status:", r.status_code)
    try:
        data = r.json()
        # Print a preview of the first few markets
        for m in data.get("data", []):
            print(f"- ID {m['id']} | {m['title']} | Status: {m['status']}")
        return data
    except ValueError:
        print("[LLMM] Raw response:", r.text)
        return {"raw": r.text}

def main():
    session = get_session()  # returns authenticated Session
    list_hourly_markets(session)

if __name__ == "__main__":
    main()
