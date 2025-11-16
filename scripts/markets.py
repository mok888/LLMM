#!/usr/bin/env python3
"""
Limitless Exchange Markets Listing
Uses the stable authentication from limitless_auth.py
"""

import json
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def list_markets(session, page=1, limit=20):
    """Fetch active markets with pagination."""
    url = f"{API_URL}/markets/active"
    params = {"page": page, "limit": limit, "sortBy": "newest"}
    r = session.get(url, params=params, timeout=30)
    print("[LLMM] Markets status:", r.status_code)
    try:
        data = r.json()
        print(json.dumps(data, indent=2)[:1000])  # preview first 1000 chars
        return data
    except ValueError:
        print("[LLMM] Raw response:", r.text)
        return {"raw": r.text}

def main():
    session = get_session()  # returns a Session object
    list_markets(session)

if __name__ == "__main__":
    main()
