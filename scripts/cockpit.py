#!/usr/bin/env python3
"""
Cockpit Script
- Reads hourly_markets.json
- Subscribes/unsubscribes to live price updates via WebSocket
"""

import asyncio
import json
import os
from websocket_client import LimitlessWebSocket  # your class from earlier

async def main():
    # Load hourly market addresses from scanner output
    if not os.path.exists("hourly_markets.json"):
        print("⚠️ No hourly_markets.json found. Run hourly_scan.py first.")
        return

    with open("hourly_markets.json") as f:
        market_addresses = json.load(f)

    print(f"[LLMM] Loading {len(market_addresses)} hourly markets from scanner output")

    private_key = os.getenv("PRIVATE_KEY")
    client = LimitlessWebSocket(private_key=private_key)

    await client.connect()
    if market_addresses:
        await client.subscribe_markets(market_addresses)
    else:
        print("⚠️ No market addresses to subscribe")

    print("📡 Listening for events... Press Ctrl+C to stop")
    await client.wait()

if __name__ == "__main__":
    asyncio.run(main())
