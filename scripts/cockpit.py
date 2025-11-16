#!/usr/bin/env python3
"""
Limitless Exchange Cockpit
- Connects to WebSocket
- Loads hourly_markets.json (conditionId → title)
- Deduplication + Refresh + Unsubscribe
- Formatted price banners
- Catch-all logger
- Heartbeat with timestamp
"""

import asyncio
import json
import os
from datetime import datetime
from custom_websocket import CustomWebSocket  # patched client

REFRESH_INTERVAL = 300  # seconds (5 minutes)

async def main():
    private_key = os.getenv("PRIVATE_KEY")
    print("=" * 50)
    print("Limitless Exchange Cockpit")
    print("=" * 50)

    client = CustomWebSocket(private_key=private_key)
    await client.connect()

    # Initial subscription
    if os.path.exists("hourly_markets.json"):
        with open("hourly_markets.json") as f:
            data = json.load(f)

        # Expect dict {conditionId: title}
        if isinstance(data, dict):
            condition_ids = list(data.keys())
            client.market_titles.update(data)
        else:
            condition_ids = data

        if condition_ids:
            await client.subscribe_markets(condition_ids)
        else:
            print("⚠️ No market addresses to subscribe")
    else:
        print("⚠️ No hourly_markets.json found")

    # Startup heartbeat
    ts = datetime.now().strftime("%H:%M %Z")
    print(f"[LLMM] Heartbeat {ts} → {len(client.subscribed_markets)} markets active, cockpit online…")

    # Start refresh loop in background
    asyncio.create_task(client.refresh_from_file("hourly_markets.json", REFRESH_INTERVAL))

    print("📡 Listening for events... Press Ctrl+C to stop")
    await client.wait()

if __name__ == "__main__":
    asyncio.run(main())