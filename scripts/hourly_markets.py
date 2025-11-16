#!/usr/bin/env python3
"""
Limitless Exchange Active Markets Scanner
"""

import json
import requests
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def scan_active_markets(session, page=1, limit=10):
    """Fetch active markets from Limitless Exchange."""
    url = f"{API_URL}/markets/active"
    params = {
        "page": str(page),
        "limit": str(limit),
        "sortBy": "newest"
    }
    r = session.get(url, params=params, timeout=30)
    print("[LLMM] Active markets status:", r.status_code)
    try:
        data = r.json()
        print(json.dumps(data, indent=2)[:1500])  # preview first 1500 chars
        return data
    except ValueError:
        print("[LLMM] Raw response:", r.text)
        return {"raw": r.text}

def main():
    session = get_session()  # reuse your authenticated session
    scan_active_markets(session)

if __name__ == "__main__":
    main()
