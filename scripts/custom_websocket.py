#!/usr/bin/env python3
"""
Custom Cockpit WebSocket Client
- Connects to Limitless Exchange
- Attempts multiple subscribe event names and payload shapes
- Binds many common event names and namespaces
- Catch-all logs top-level keys, full JSON, recursively finds odds-like objects
- Heartbeat, periodic probe, silence monitor, clean disconnect
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
        self.subscribed_markets = []  # marketAddresses or ids
        self.market_titles = {}       # address/id -> title
        self.last_non_system_event_ts = None

        self.sio = socketio.AsyncClient(
            logger=verbose_logs,
            engineio_logger=verbose_logs
        )
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup event handlers for /markets and helpful fallbacks"""

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

        # Common price event names
        @self.sio.event(namespace="/markets")
        async def newPriceData(data):
            await self._print_price_banner(data)

        @self.sio.event(namespace="/markets")
        async def marketPriceData(data):
            await self._print_price_banner(data)

        @self.sio.event(namespace="/markets")
        async def priceUpdate(data):
            await self._print_price_banner(data)

        @self.sio.event(namespace="/markets")
        async def prices(data):
            await self._print_price_banner(data)

        @self.sio.event(namespace="/markets")
        async def market_update(data):
            await self._print_price_banner(data)

        # Generic handlers and catch-all
        @self.sio.event(namespace="/markets")
        async def data(data):
            await self._maybe_highlight_and_dump("data", data, ns="/markets")

        @self.sio.event(namespace="/markets")
        async def update(data):
            await self._maybe_highlight_and_dump("update", data, ns="/markets")

        @self.sio.event(namespace="/markets")
        async def message(data):
            await self._maybe_highlight_and_dump("message", data, ns="/markets")

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

        # ===== Extra namespace fallback: /prices =====
        try:
            @self.sio.event(namespace="/prices")
            async def connect_prices():
                print("✅ Connected to /prices")
        except Exception:
            pass

        try:
            @self.sio.on("*", namespace="/prices")
            async def catch_all_prices(event, data):
                await self._maybe_highlight_and_dump(event, data, ns="/prices")
        except Exception:
            pass

    async def _maybe_highlight_and_dump(self, event, data, ns):
        """Dump event payload, print keys, and recursively find any odds-like objects"""
        try:
            if event != "system":
                self.last_non_system_event_ts = time()

            if isinstance(data, dict):
                keys = list(data.keys())
                print(f"[LLMM] {ns} Raw event: {event} | Keys: {keys}")
            else:
                print(f"[LLMM] {ns} Raw event: {event} | Non-dict payload")

            try:
                payload = json.dumps(data, indent=2, sort_keys=True)
            except Exception:
                payload = str(data)
            print(payload)

            def find_odds(obj, path="root"):
                found = []
                if isinstance(obj, dict):
                    cid = (obj.get("conditionId") or obj.get("condition_id") or obj.get("marketAddress")
                           or obj.get("address") or obj.get("id") or obj.get("market"))
                    prices = (obj.get("prices") or obj.get("price") or obj.get("odds")
                              or obj.get("pricesFormatted") or obj.get("bestPrices") or obj.get("outcomesPrices"))
                    if cid and prices:
                        found.append((path, cid, prices, obj))
                    # outcomes array with price objects
                    if isinstance(obj.get("outcomes"), list):
                        for i, out in enumerate(obj["outcomes"]):
                            if isinstance(out, dict):
                                out_cid = out.get("conditionId") or out.get("id") or out.get("label")
                                out_prices = out.get("prices") or out.get("price") or out.get("odds")
                                if out_cid and out_prices:
                                    found.append((f"{path}.outcomes[{i}]", out_cid, out_prices, out))
                    for k, v in obj.items():
                        new_path = f"{path}.{k}"
                        found.extend(find_odds(v, new_path))
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_path = f"{path}[{i}]"
                        found.extend(find_odds(item, new_path))
                return found

            matches = find_odds(data)
            if isinstance(data, dict) and "markets" in data and not matches:
                matches.extend(find_odds(data["markets"], path="root.markets"))

            for path, cid, prices, raw in matches:
                yes, no = ("?", "?")
                if isinstance(prices, list) and len(prices) >= 2:
                    yes, no = prices[0], prices[1]
                elif isinstance(prices, (str, int, float)):
                    yes = prices
                title = self.market_titles.get(cid, (cid[:6] + "…") if isinstance(cid, str) else str(cid))
                print(f"[LLMM] 🔎 Detected odds at {ns}:{event}:{path} → {title} | YES={yes} | NO={no}")
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
            cid = data.get("conditionId") or data.get("condition_id") or data.get("marketAddress") or data.get("id")
            prices = data.get("prices") or data.get("price") or data.get("odds")
            vol = data.get("volumeFormatted") or data.get("volume")

            if not cid and "markets" in data and isinstance(data["markets"], list) and data["markets"]:
                m0 = data["markets"][0]
                if isinstance(m0, dict):
                    cid = m0.get("conditionId") or m0.get("id") or cid
                    prices = m0.get("prices") or m0.get("price") or prices
                    vol = m0.get("volumeFormatted") or m0.get("volume") or vol

        yes, no = ("?", "?")
        if isinstance(prices, list) and len(prices) >= 2:
            yes, no = prices[0], prices[1]
        elif isinstance(prices, (str, int, float)):
            yes = prices

        title = self.market_titles.get(cid, (cid[:6] + "…") if isinstance(cid, str) else "Unknown")
        print(f"[LLMM] {title} → YES={yes} | NO={no} | Vol={vol}")

    async def connect(self, timeout=10, retries=3, retry_delay=3):
        """Connect with timeout, retries and explicit headers to satisfy the server upgrade"""
        print(f"🔌 Connecting to {self.websocket_url}... (timeout={timeout}s, retries={retries})")
        connect_options = {"transports": ["websocket"]}

        headers = {
            "Origin": "https://limitless.exchange",
            "User-Agent": "LLMM/1.0"
        }
        if self.session_cookie:
            headers["Cookie"] = f"limitless_session={self.session_cookie}"
        connect_options["headers"] = headers

        attempt = 0
        while attempt < retries:
            attempt += 1
            try:
                coro = self.sio.connect(self.websocket_url, namespaces=["/markets"], **connect_options)
                await asyncio.wait_for(coro, timeout=timeout)
                await asyncio.sleep(0.5)
                if self.connected:
                    print("✅ Successfully connected")
                    return
                else:
                    print(f"❌ Connect attempt {attempt} completed but 'connected' flag is False")
            except asyncio.TimeoutError:
                print(f"⏱️ Connect attempt {attempt} timed out after {timeout}s")
            except Exception as e:
                print(f"⚠️ Connect attempt {attempt} raised: {type(e).__name__}: {e}")
            if attempt < retries:
                print(f"↺ Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)

        raise ConnectionError(f"Failed to connect to {self.websocket_url} after {retries} attempts")

    async def subscribe_markets(self, condition_ids):
        """Subscribe to markets — emit marketAddresses and a set of common fallback subscribe events"""
        if not self.connected:
            print("❌ Not connected")
            return

        condition_ids = list(dict.fromkeys(condition_ids))
        payload_addresses = {"marketAddresses": condition_ids}
        payload_conditions = {"conditionIds": condition_ids}
        payload_simple = {"markets": condition_ids}

        print(f"[LLMM] Emitting subscribe_market_prices with payload: {payload_addresses}")
        await self.sio.emit("subscribe_market_prices", payload_addresses, namespace="/markets")

        # Emit safe fallbacks (server will ignore unknown events)
        fallbacks = [
            ("subscribe_markets", payload_addresses),
            ("subscribe", payload_addresses),
            ("subscribePrices", payload_addresses),
            ("subscribe_market", payload_addresses),
            ("subscribe_market_prices_v2", payload_addresses),
            ("subscribe_market_prices", payload_conditions),
            ("subscribe_market_prices", payload_simple),
        ]
        for ev, payload in fallbacks:
            try:
                await self.sio.emit(ev, payload, namespace="/markets")
                print(f"[LLMM] Emitted fallback subscribe event: {ev}")
            except Exception as e:
                print(f"[LLMM] Fallback emit {ev} failed: {e}")

        if self.session_cookie:
            try:
                await self.sio.emit("subscribe_positions", payload_addresses, namespace="/markets")
            except Exception:
                pass

        print(f"[LLMM] Subscribed to {len(condition_ids)} markets (attempted multiple names)")
        self.subscribed_markets = condition_ids

    async def unsubscribe_markets(self, condition_ids):
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
        while True:
            try:
                if not self.subscribed_markets:
                    await asyncio.sleep(interval)
                    continue

                payload = {
                    "marketAddresses": self.subscribed_markets,
                    "marketSlugs": []
                }

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
        try:
            await self.sio.disconnect()
            print("🔌 Disconnected cleanly")
        except Exception as e:
            print(f"⚠️ Error during disconnect: {e}")
