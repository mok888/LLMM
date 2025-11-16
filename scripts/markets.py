#!/usr/bin/env python3
"""
Limitless Exchange Markets Listing
Uses the stable authentication from limitless_auth.py
"""

import json
from limitless_auth import main as auth_main  # reuse your working auth script
import requests

API_URL = "https://api.limitless.exchange"

def list_markets(session, page=1, limit=20):
    """Fetch active markets with pagination."""
    url = f"{API_URL}/markets/active"
    params = {"page": page, "limit": limit, "sortBy": "newest"}
    r = session.get(url, params=params, timeout=30)
    print("[LLMM] Markets status:", r.status_code)
    try:
        data = r.json()
        print(json.dumps(data, indent=2)[:1000])  # print first 1000 chars
        return data
    except ValueError:
        print("[LLMM] Raw response:", r.text)
        return {"raw": r.text}

def main():
    # Get authenticated session from your auth script
    session = auth_main()  # returns a requests.Session with cookie
    list_markets(session)

if __name__ == "__main__":
    main()
