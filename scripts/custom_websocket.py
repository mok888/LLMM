#!/usr/bin/env python3
"""
Custom Cockpit WebSocket Client
- Connects to Limitless Exchange
- Handles subscriptions, odds updates, and lifecycle banners
- Heartbeat with timestamp
- Catch-all logger dumps full JSON payloads
"""

import asyncio
import json
import os
import socketio
from datetime import datetime

class CustomWebSocket:
    def __init__(self, websocket_url="wss://ws.limitless.exchange", private_key=None):
        self.websocket_url = websocket_url
        self.private_key = private_key
        self.session_cookie = None
        self.connected = False
        self.subscribed_markets = []
        self.market_titles = {}  # conditionId → title
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup event handlers"""

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

        @self.sio.event(namespace="/markets")
        async def newPriceData(data):
            """Formatted price banner"""
            cid = data.get("conditionId")
            prices = data.get("prices", [])
            vol = data.get("volumeFormatted") or data.get("volume")

            yes, no = ("?", "?")
            if len(prices) == 2:
                yes, no = prices

            title = self.market_titles.get(cid, cid[:6] + "…")
            print(f"[LLMM] {title} → YES={yes} | NO={no} | Vol={vol}")

        @self.sio.event(namespace="/markets")
        async def positions(data):
            account = data.get("account")
            positions = data.get("positions", [])
            print(f"[LLMM] User {account} has {len(positions)} positions")

        @self.sio.event(namespace="/markets")
        async def exception(data):
            print(f"[LLMM] Exception: {json.dumps(data)}")

        # Catch-all logger: dump full JSON payload
        @self.sio.on("*", namespace="/markets")
        async def catch_all(event, data):
            try:
                payload = json.dumps(data, indent=2, sort_keys=True)
                print(f"[LLMM] Raw event: {event}\n{payload}")
            except Exception as e:
                print(f"[LLMM] Raw event: {event} (unserializable) → {data} | Error: {e}")

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
        """Subscribe to markets"""
        if not self.connected:
            print("❌ Not connected")
            return

        condition_ids = list(dict.fromkeys(condition_ids))  # deduplicate
        payload = {"marketAddresses": condition_ids}
        await self.sio.emit("subscribe_market_prices", payload, namespace="/markets")
        print(f"[LLMM] Subscribed to {len(condition_ids)} markets")

        if self.session_cookie:
            await self.sio.emit("subscribe_positions", payload, namespace="/markets")

        self.subscribed