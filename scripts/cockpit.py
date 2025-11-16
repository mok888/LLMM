#!/usr/bin/env python3
"""
Cockpit Script with Integrated Refresh + Deduplication + Unsubscribe
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
    """Reload hourly_markets.json and adjust subscriptions periodically"""
    while True:
        try:
            if os.path.exists("hourly_markets.json"):
                with open("hourly_markets.json") as f:
                    new_addresses = json.load(f)

                new_addresses = deduplicate(new_addresses)

                # Current subscribed set
                current_set = set(client.subscribed_markets)
                new_set = set(new_addresses)

                # Find additions and removals
                to_add = list(new_set - current_set)
                to_remove = list(current_set - new_set)

                if to_add:
                    print(f"[LLMM] Adding {len(to_add)} new markets → {to_add}")
                    await client.subscribe_markets(to_add)

                if to_remove:
                    print(f"[LLMM] Removing {len(to_remove)} markets → {to_remove}")
                    # Emit unsubscribe events
                    payload = {'marketAddresses': to_remove}
                    await client.sio.emit('unsubscribe_market_prices', payload, namespace='/markets')
                    if client.session_cookie:
                        await client.sio.emit('unsubscribe_positions', payload, namespace='/markets')
                    # Update local tracking
                    client.subscribed_markets = [addr for addr in client.subscribed_markets if addr not in to_remove]

                if not to_add and not to_remove:
                    print("[LLMM] Subscriptions already up-to-date")

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
