#!/usr/bin/env python3
"""
Limitless Exchange Crypto Markets Scanner
"""

import json
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def list_crypto_markets(session, page=1, limit=50):
    """Fetch all active markets and filter for Crypto category."""
    url = f"{API_URL}/markets/active"
    params = {"page": page, "limit": limit, "sortBy": "newest"}
    r = session.get(url, params=params, timeout=30)
    print("[LLMM] Markets status:", r.status_code)
    try:
        data = r.json()
        crypto = []
        for m in data.get("data", []):
            cats = m.get("categories", [])
            if any(c.lower() == "crypto" for c in cats):
                crypto.append(m)
        print(f"[LLMM] Found {len(crypto)} crypto markets")
        for m in crypto:
            print(f"- ID {m['id']} | {m['title']} | Status: {m['status']}")
        return crypto
    except ValueError:
        print("[LLMM] Raw response:", r.text)
        return []

def main():
    session = get_session()
    list_crypto_markets(session)

if __name__ == "__main__":
    main()
