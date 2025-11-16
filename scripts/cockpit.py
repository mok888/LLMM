#!/usr/bin/env python3
"""
Limitless Exchange Cockpit
- Starts the CustomWebSocket client
- Loads hourly_markets.json and subscribes
- Starts refresh, probe, and silence monitor tasks
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from custom_websocket import CustomWebSocket

REFRESH_INTERVAL = 300  # seconds

async def main():
    private_key = os.getenv("PRIVATE_KEY")
    print("=" * 50)
    print("Limitless Exchange Cockpit")
    print("=" * 50)

    verbose = "--verbose" in sys.argv
    client = CustomWebSocket(private_key=private_key, verbose_logs=verbose)

    try:
        await client.connect()

        condition_ids = []
        if os.path.exists("hourly_markets.json"):
            with open("hourly_markets.json") as f:
                data = json.load(f)
            if isinstance(data, dict):
                condition_ids = list(data.keys())
                client.market_titles.update(data)
            else:
                condition_ids = data

        if condition_ids:
            await client.subscribe_markets(condition_ids)
        else:
            print("⚠️ No market addresses to subscribe")

        ts = datetime.now().strftime("%H:%M %Z")
        print(f"[LLMM] Heartbeat {ts} → {len(client.subscribed_markets)} markets active, cockpit online…")

        asyncio.create_task(client.refresh_from_file("hourly_markets.json", REFRESH_INTERVAL))
        asyncio.create_task(client.periodic_probe(60))
        asyncio.create_task(client.monitor_silence(300))

        print("📡 Listening for events... Press Ctrl+C to stop")
        await client.wait()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
