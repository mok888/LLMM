#!/usr/bin/env python3
"""
WebSocket client for Limitless Exchange
"""

import asyncio
import json
import socketio
from typing import Optional, List

class LimitlessWebSocket:
    def __init__(self, websocket_url: str = "wss://ws.limitless.exchange", private_key: Optional[str] = None):
        self.websocket_url = websocket_url
        self.private_key = private_key
        self.session_cookie = None
        self.connected = False
        self.subscribed_markets: List[str] = []
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self._setup_handlers()

    # … keep the rest of your class implementation here …
