#!/usr/bin/env python3
"""
Custom Cockpit WebSocket Client
- Deduplication
- Refresh + Unsubscribe
- Formatted price banners
- Title lookup from scanner payload
- Catch-all logger
- Heartbeat with timestamp
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

            # ✅ Fixed fallback line
            title = self.market_titles.get(cid, cid[:6] + "…")
            print(f"[LLMM] {title} → YES={yes} | NO={no} | Vol={vol}")

        @self.sio.event