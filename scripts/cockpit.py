#!/usr/bin/env python3
"""
Cockpit Script with Integrated Refresh + Deduplication
"""

import asyncio
import json
import os
from websocket_client import LimitlessWebSocket

REFRESH_INTERVAL = 300  # seconds (5 minutes)

def deduplicate(addresses):
    """Remove duplicates while preserving order"""
    seen = set()
    unique = []
    for addr in addresses:
        if addr and addr not in seen:
            seen.add(addr)
            unique.append(addr)
    return unique

async def refresh_markets(client):
    """Reload hourly_markets.json and resubscribe periodically"""
    while True:
        try:
            if os.path.exists("hourly_markets.json"):
                with open("hourly_markets.json") as f:
                    market_addresses = json.load(f)

                # Deduplicate before subscribing
                market_addresses = deduplicate(market_addresses)

                if market_addresses:
                    print(f"[LLMM] Refreshing subscriptions → {len(market_addresses)} unique markets")
                    await client.subscribe_markets(market_addresses)
                else:
                    print("[LLMM] Refresh file found but empty")
            else:
                print("[LLMM] No hourly_markets.json found. Run scanner first.")

        except Exception as e:
            print(f"[LLMM] Refresh error: {e}")

        await asyncio.sleep(REFRESH_INTERVAL)

async def main():
    private_key = os.getenv("PRIVATE_KEY")
    print("=" * 50)
    print("Limitless Exchange Cockpit")
    print("=" * 50)

    client = LimitlessWebSocket(private_key=private_key)
    await client.connect()

    # Initial subscription
    if os.path.exists("hourly_markets.json"):
        with open("hourly_markets.json") as f:
            market_addresses = json.load(f)
        market_addresses = deduplicate(market_addresses)
        if market_addresses:
            await client.subscribe_markets(market_addresses)
        else:
            print("⚠️ No market addresses to subscribe")
    else:
        print("⚠️ No hourly_markets.json found")

    # Start refresh loop in background
    asyncio.create_task(refresh_markets(client))

    print("📡 Listening for events... Press Ctrl+C to stop")
    await client.wait()

if __name__ == "__main__":
    asyncio.run(main())
