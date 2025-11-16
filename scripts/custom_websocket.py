#!/usr/bin/env python3
"""
Custom Cockpit WebSocket Client
- Connects to Limitless Exchange
- Subscriptions with marketAddresses payload (fallback commented)
- Formatted price banners for multiple event names
- Catch-all logs top-level keys, full JSON, recursively finds odds-like objects
- Root namespace fallbacks to capture emissions on "/"
- Heartbeat with timestamp
- Periodic probe to request snapshots/pings (server-tolerant)
- Silence monitor warns if no non-system events arrive
- Clean disconnect
"""

import asyncio
import json
import os
import socketio
from datetime import datetime
from time import time

class CustomWebSocket:
    def __init__(self, websocket_url="wss://ws.limitless.exchange", private_key=None, verbose_logs=True):
        self.websocket_url = websocket_url
        self.private_key = private_key
        self.session_cookie = None
        self.connected = False
        self.subscribed_markets = []  # conditionIds or addresses (hashes)
        self.market_titles = {}       # conditionId → title
        self.last_non_system_event_ts = None

        # Toggle transport logs for debugging mapping issues
        self.sio = socketio.AsyncClient(
            logger=verbose_logs,
            engineio_logger=verbose_logs
        )
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup event handlers"""

        # ===== Namespace: /markets =====
        @self.sio.event(namespace="/markets")
        async def connect():
            self.connected = True
            print("✅ Connected to /markets")
            if self.session_cookie:
                await self.sio.emit("authenticate", f"Bearer {self.session_cookie}", namespace="/markets")
            if self.subscribed_markets:
                await asyncio.sleep(1)
                await self._resubscribe()

        @self.sio.event(namespace="/markets")
        async def disconnect():
            self.connected = False
            print("❌ Disconnected from /markets")

        @self.sio.event(namespace="/markets")
        async def system(data):
            print(f"[LLMM] System: {json.dumps(data)}")

        # Odds handlers — cover common names
        @self.sio.event(namespace="/markets")
        async def newPriceData(data):
            await self._print_price_banner(data)

        @self.sio.event(namespace="/markets")
        async def marketPriceData(data):
            await self._print_price_banner(data)

        @self.sio.event(namespace="/markets")
        async def priceUpdate(data):
            await self._print_price_banner(data)

        # Generic handlers that some servers use
        @self.sio.event(namespace="/markets")
        async def data(data):
            await self._maybe_highlight_and_dump("data", data, ns="/markets")

        @self.sio.event(namespace="/markets")
        async def update(data):
            await self._maybe_highlight_and_dump("update", data, ns="/markets")

        @self.sio.event(namespace="/markets")
        async def message(data):
            await self._maybe_highlight_and_dump("message", data, ns="/markets")

        # Catch-all logger: dump full JSON, keys, and highlight odds
        @self.sio.on("*", namespace="/markets")
        async def catch_all(event, data):
            await self._maybe_highlight_and_dump(event, data, ns="/markets")

        # ===== Root namespace (/) fallbacks =====
        @self.sio.event
        async def message(data):
            await self._maybe_highlight_and_dump("message", data, ns="/")

        @self.sio.on("*")
        async def catch_all_root(event, data):
            await self._maybe_highlight_and_dump(event, data, ns="/")

    async def _maybe_highlight_and_dump(self, event, data, ns):
        """Dump event payload, print keys, and recursively find any odds objects"""
        try:
            # Mark last non-system event
            if event != "system":
                self.last_non_system_event_ts = time()

            # Keys summary
            if isinstance(data, dict):
                keys = list(data.keys())
                print(f"[LLMM] {ns} Raw event: {event} | Keys: {keys}")
            else:
                print(f"[LLMM] {ns} Raw event: {event} | Non-dict payload")

            # Full JSON dump (safe fallback for non-serializable)
            try:
                payload = json.dumps(data, indent=2, sort_keys=True)
            except Exception:
                payload = str(data)
            print(payload)

            # Recursive scan for odds-like objects
            def find_odds(obj, path="root"):
                found = []
                if isinstance(obj, dict):
                    # direct match
                    cid = obj.get("conditionId") or obj.get("condition_id") or obj.get("id")
                    prices = obj.get("prices") or obj.get("price") or obj.get("odds") or obj.get("pricesFormatted")
                    if cid and prices:
                        found.append((path, cid, prices, obj))
                    # descend into children
                    for k, v in obj.items():
                        new_path = f"{path}.{k}"
                        found.extend(find_odds(v, new_path))
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_path = f"{path}[{i}]"
                        found.extend(find_odds(item, new_path))
                return found

            matches = find_odds(data)
            # also check common top-level "markets" list if not already matched
            if isinstance(data, dict) and "markets" in data and not matches:
                matches.extend(find_odds(data["markets"], path="root.markets"))

            for path, cid, prices, raw in matches:
                # normalize prices list if possible
                yes, no = ("?", "?")
                if isinstance(prices, list) and len(prices) >= 2:
                    yes, no = prices[0], prices[1]
                elif isinstance(prices, (str, int, float)):
                    yes = prices
                title = self.market_titles.get(cid, cid[:6] + "…") if isinstance(cid, str) else str(cid)
                print(f"[LLMM] 🔎 Detected odds at {ns}:{event}:{path} → {title} | YES={yes} | NO={no}")
                # print raw snippet for operator clarity (compact)
                try:
                    snippet = json.dumps(raw, indent=2, sort_keys=True)
                except Exception:
                    snippet = str(raw)
                print(snippet)

        except Exception as e:
            print(f"[LLMM] {ns} Raw event: {event} (unserializable) → {data} | Error: {e}")

    async def _print_price_banner(self, data):
        """Shared odds banner printer"""
        cid = None
        prices = None
        vol = None

        if isinstance(data, dict):
            cid = data.get("conditionId")
            prices = data.get("prices", [])
            vol = data.get("volumeFormatted") or data.get("volume")

            # handle nested market object
            if not cid and "markets" in data and isinstance(data["markets"], list) and data["markets"]:
                m0 = data["markets"][0]
                if isinstance(m0, dict):
                    cid = m0.get("conditionId") or cid
                    prices = m0.get("prices", prices)
                    vol = m0.get("volume