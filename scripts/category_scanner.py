#!/usr/bin/env python3
"""
Limitless Exchange Category Scanner
Uses category IDs to fetch and filter active markets.
"""

import json
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def get_categories(session):
    url = f"{API_URL}/markets/categories/count"
    r = session.get(url, timeout=30)
    data = r.json()
    return [cat["id"] for cat in data.get("categories", [])]

def get_markets_by_category(session, category, limit=50):
    url = f"{API_URL}/markets/active"
    params = {"category": category, "limit": str(limit)}
    r = session.get(url, params=params, timeout=30)
    return r.json().get("data", [])

def main():
    session = get_session()
    categories = get_categories(session)
    print("[LLMM] Categories discovered:", categories)

    # Example: scan crypto only
    crypto_markets = get_markets_by_category(session, "crypto")
    print("[LLMM] Crypto markets:")
    for m in crypto_markets:
        print(f"- {m['title']} | ID {m['id']} | Deadline {m['expirationDate']}")

    # Example: filter BTC/ETH only
    btc_eth = [m for m in crypto_markets if m.get("ticker") in ("BTC","ETH")]
    print("[LLMM] BTC/ETH markets:")
    for m in btc_eth:
        print(f"- {m['ticker']} | {m['title']} | Deadline {m['expirationDate']}")

if __name__ == "__main__":
    main()
