#!/usr/bin/env python3
"""
Cockpit Script
- Reads hourly_markets.json
- Prints lifecycle banners for new/removed markets
- Subscribes/unsubscribes to live price updates via WebSocket
"""

import asyncio
import json
import websockets
import os

API_WS_URL = "wss://api.limitless.exchange/ws"

async def cockpit():
    last_ids = set()
    subscribed = set()

    async with websockets.connect(API_WS_URL) as ws:
        while True:
            # Load latest discovery file
            if os.path.exists("hourly_markets.json"):
                with open("hourly_markets.json") as f:
                    markets = json.load(f)
                current_ids = {m["id"] for m in markets}

                # Lifecycle banners
                new_ids = current_ids - last_ids
                removed_ids = last_ids - current_ids

                if new_ids:
                    print(f"[LLMM] NEW hourly markets discovered:")
                    for m in markets:
                        if m["id"] in new_ids:
                            title = m.get("title") or "N/A"
                            deadline = m.get("expirationDate") or "N/A"
                            print(f"    + {m['id']} | {title} | Deadline {deadline}")

                if removed_ids:
                    print(f"[LLMM] REMOVED hourly markets:")
                    for mid in removed_ids:
                        print(f"    - {mid}")

                # Subscribe to new IDs
                for mid in new_ids:
                    if mid not in subscribed:
                        sub_msg = {"type": "subscribe", "channel": "market", "id": mid}
                        await ws.send(json.dumps(sub_msg))
                        print(f"[LLMM] Subscribed to market {mid}")
                        subscribed.add(mid)

                # Unsubscribe from removed IDs
                for mid in removed_ids:
                    if mid in subscribed:
                        unsub_msg = {"type": "unsubscribe", "channel": "market", "id": mid}
                        await ws.send(json.dumps(unsub_msg))
                        print(f"[LLMM] Unsubscribed from market {mid}")
                        subscribed.remove(mid)

                last_ids = current_ids

            # Listen for live updates
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(msg)
                if "marketId" in data:
                    mid = data["marketId"]
                    prices = data.get("prices")
                    volume = data.get("volume")
                    print(f"[LLMM] Market {mid} update → Prices {prices} | Volume {volume}")
            except asyncio.TimeoutError:
                # No message in 5s, loop back to reload file
                pass

if __name__ == "__main__":
    asyncio.run(cockpit())
