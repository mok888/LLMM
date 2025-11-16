#!/usr/bin/env python3
"""
Custom Cockpit WebSocket Client
- Connects to Limitless Exchange
- Subscriptions with marketAddresses payload (fallback commented)
- Formatted price banners for multiple event names
- Catch-all logs top-level keys, full JSON, and highlights odds if present
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
        """Dump event payload, print keys, and highlight odds if present"""
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

            # Full JSON dump
            try:
                payload = json.dumps(data, indent=2, sort_keys=True)
            except Exception:
                payload = str(data)
            print(payload)

            # Highlight odds if present at top-level
            if isinstance(data, dict):
                cid = data.get("conditionId")
                prices = data.get("prices")
                # also check common nesting patterns
                if not cid and "markets" in data and isinstance(data["markets"], list) and data["markets"]:
                    m0 = data["markets"][0]
                    if isinstance(m0, dict):
                        cid = m0.get("conditionId") or cid
                        prices = m0.get("prices") or prices

                if cid and prices:
                    yes, no = ("?", "?")
                    if isinstance(prices, list) and len(prices) == 2:
                        yes, no = prices
                    title = self.market_titles.get(cid, cid[:6] + "…")
                    print(f"[LLMM] 🔎 Detected odds in {ns}:{event}: {title} → YES={yes} | NO={no}")
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
                    vol = m0.get("volumeFormatted") or m0.get("volume") or vol

        yes, no = ("?", "?")
        if isinstance(prices, list) and len(prices) == 2:
            yes, no = prices

        title = self.market_titles.get(cid, cid[:6] + "…") if cid else "Unknown"
        print(f"[LLMM] {title} → YES={yes} | NO={no} | Vol={vol}")

    async def connect(self):
        print(f"🔌 Connecting to {self.websocket_url}...")
        connect_options = {"transports": ["websocket"]}
        if self.session_cookie:
            connect_options["headers"] = {"Cookie": f"limitless_session={self.session_cookie}"}
        await self.sio.connect(self.websocket_url, namespaces=["/markets"], **connect_options)
        await asyncio.sleep(0.5)
        if self.connected:
            print("✅ Successfully connected")
        else:
            print("❌ Connection failed")

    async def subscribe_markets(self, condition_ids):
        """Subscribe to markets — emit only marketAddresses by default to avoid server confusion"""
        if not self.connected:
            print("❌ Not connected")
            return

        condition_ids = list(dict.fromkeys(condition_ids))  # deduplicate

        payload_addresses = {"marketAddresses": condition_ids}

        print(f"[LLMM] Emitting subscribe_market_prices with payload: {payload_addresses}")
        await self.sio.emit("subscribe_market_prices", payload_addresses, namespace="/markets")

        # Uncomment the next block only if you confirm the server needs 'conditionIds'
        # payload_conditions = {"conditionIds": condition_ids}
        # print(f"[LLMM] Emitting (fallback) subscribe_market_prices with payload: {payload_conditions}")
        # await self.sio.emit("subscribe_market_prices", payload_conditions, namespace="/markets")

        if self.session_cookie:
            await self.sio.emit("subscribe_positions", payload_addresses, namespace="/markets")

        print(f"[LLMM] Subscribed to {len(condition_ids)} markets")
        self.subscribed_markets = condition_ids

    async def unsubscribe_markets(self, condition_ids):
        """Unsubscribe from markets"""
        payload = {"marketAddresses": condition_ids}
        await self.sio.emit("unsubscribe_market_prices", payload, namespace="/markets")
        if self.session_cookie:
            await self.sio.emit("unsubscribe_positions", payload, namespace="/markets")
        print(f"[LLMM] Unsubscribed {len(condition_ids)} markets")

        self.subscribed_markets = [cid for cid in self.subscribed_markets if cid not in condition_ids]

    async def _resubscribe(self):
        if self.subscribed_markets:
            await self.subscribe_markets(self.subscribed_markets)

    async def refresh_from_file(self, filename="hourly_markets.json", interval=300):
        """Reload scanner output and sync subscriptions"""
        while True:
            try:
                if os.path.exists(filename):
                    with open(filename) as f:
                        data = json.load(f)

                    if isinstance(data, dict):
                        new_ids = list(data.keys())
                        self.market_titles.update(data)
                    else:
                        new_ids = data

                    new_ids = list(dict.fromkeys(new_ids))
                    current_set = set(self.subscribed_markets)
                    new_set = set(new_ids)

                    to_add = list(new_set - current_set)
                    to_remove = list(current_set - new_set)

                    if to_add:
                        print(f"[LLMM] Adding {len(to_add)} markets")
                        await self.subscribe_markets(to_add)
                    if to_remove:
                        print(f"[LLMM] Removing {len(to_remove)} markets")
                        await self.unsubscribe_markets(to_remove)
                    if not to_add and not to_remove:
                        print(f"[LLMM] Subscriptions already up-to-date ({len(new_ids)} markets)")

                    ts = datetime.now().strftime("%H:%M %Z")
                    print(f"[LLMM] Heartbeat {ts} → {len(self.subscribed_markets)} markets active, still listening…")

                else:
                    print("[LLMM] No hourly_markets.json found")

            except Exception as e:
                print(f"[LLMM] Refresh error: {e}")

            await asyncio.sleep(interval)

    async def periodic_probe(self, interval=60):
        """Periodically request snapshots/pings; include server-tolerant payloads and swallow harmless server errors"""
        while True:
            try:
                if not self.subscribed_markets:
                    await asyncio.sleep(interval)
                    continue

                # Include only accepted keys (marketAddresses) and safe extras
                payload = {
                    "marketAddresses": self.subscribed_markets,
                    "marketSlugs": []  # harmless if unused
                }

                # Try a list of common probe event names; server will respond or error
                for ev in ("request_market_snapshot", "ping_prices", "requestPrices"):
                    try:
                        await self.sio.emit(ev, payload, namespace="/markets")
                        print(f"[LLMM] Probe → emitted {ev} for {len(self.subscribed_markets)} markets")
                    except Exception as inner:
                        print(f"[LLMM] Probe emit {ev} error: {inner}")

            except Exception as e:
                print(f"[LLMM] Probe error: {e}")
            await asyncio.sleep(interval)

    async def monitor_silence(self, warn_after=300):
        """Warn if we haven't seen non-system events for too long"""
        while True:
            if self.last_non_system_event_ts is None:
                print("[LLMM] Silence monitor: no non-system events observed yet")
            else:
                delta = time() - self.last_non_system_event_ts
                if delta > warn_after:
                    print(f"[LLMM] Warning: {int(delta)}s without non-system events")
            await asyncio.sleep(30)

    async def wait(self):
        await self.sio.wait()

    async def close(self):
        """Clean disconnect"""
        try:
            await self.sio.disconnect()
            print("🔌 Disconnected cleanly")
        except Exception as e:
            print(f"⚠️ Error during disconnect: {e}")
