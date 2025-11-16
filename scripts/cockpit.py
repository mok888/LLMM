#!/usr/bin/env python3
"""
Limitless Exchange WebSocket Client - Streamlined Example
Connect to real-time market data and position updates
"""

import asyncio
import json
import logging
import os
from typing import Optional, List

import socketio
from common_utils import authenticate, get_signing_message

logging.basicConfig(level=logging.WARNING, format='%(message)s')
logger = logging.getLogger(__name__)

##### Global configuration
MARKET_ADDRESSES = ["0x..."]  # Replace with actual hourly market addresses

class LimitlessWebSocket:
    """
    Streamlined WebSocket client for Limitless Exchange
    Handles authentication, connection, subscription, and events
    """

    def __init__(self, websocket_url: str = "wss://ws.limitless.exchange", private_key: Optional[str] = None):
        self.websocket_url = websocket_url
        self.private_key = private_key
        self.session_cookie = None
        self.connected = False
        self.subscribed_markets: List[str] = []
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup essential event handlers"""

        @self.sio.event(namespace='/markets')
        async def connect():
            self.connected = True
            print("✅ Connected to /markets")
            if self.session_cookie:
                await self.sio.emit('authenticate', f'Bearer {self.session_cookie}', namespace='/markets')
            if self.subscribed_markets:
                await asyncio.sleep(1)
                await self._resubscribe()

        @self.sio.event(namespace='/markets')
        async def disconnect():
            self.connected = False
            print("❌ Disconnected from /markets")

        @self.sio.event(namespace='/markets')
        async def authenticated(data):
            print(f"[LLMM] Authenticated: {json.dumps(data)}")

        @self.sio.event(namespace='/markets')
        async def newPriceData(data):
            print(f"[LLMM] Price update: {json.dumps(data)}")

        @self.sio.event(namespace='/markets')
        async def positions(data):
            print(f"[LLMM] Positions: {json.dumps(data)}")

        @self.sio.event(namespace='/markets')
        async def system(data):
            print(f"[LLMM] System: {json.dumps(data)}")

        @self.sio.event(namespace='/markets')
        async def exception(data):
            print(f"[LLMM] Exception: {json.dumps(data)}")

    async def authenticate(self):
        """Get session cookie for authentication"""
        if not self.private_key:
            print("💡 No private key - running in public mode")
            return
        try:
            print("🔐 Authenticating with private key...")
            signing_message = get_signing_message()
            self.session_cookie, user_data = authenticate(self.private_key, signing_message)
            print(f"✅ Authenticated as: {user_data['account']}")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")

    async def connect(self):
        """Connect to WebSocket"""
        await self.authenticate()
        print(f"🔌 Connecting to {self.websocket_url}...")
        connect_options = {'transports': ['websocket']}
        if self.session_cookie:
            connect_options['headers'] = {'Cookie': f'limitless_session={self.session_cookie}'}
            print("🍪 Adding session cookie to connection headers")
        await self.sio.connect(self.websocket_url, namespaces=['/markets'], **connect_options)
        await asyncio.sleep(0.5)
        if self.connected:
            print("✅ Successfully connected")
        else:
            print("❌ Connection failed")

    async def subscribe_markets(self, market_addresses: List[str]):
        """Subscribe to market price updates"""
        if not self.connected:
            print("❌ Not connected - call connect() first")
            return
        print(f"📊 Subscribing to {len(market_addresses)} markets")
        payload = {'marketAddresses': market_addresses}
        await self.sio.emit('subscribe_market_prices', payload, namespace='/markets')
        print("✅ Subscribed to market prices")
        if self.session_cookie:
            await self.sio.emit('subscribe_positions', payload, namespace='/markets')
            print("✅ Subscribed to positions")
        self.subscribed_markets.extend(addr for addr in market_addresses if addr not in self.subscribed_markets)

    async def _resubscribe(self):
        """Re-subscribe after reconnection"""
        if self.subscribed_markets:
            await self.subscribe_markets(self.subscribed_markets)

    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.connected:
            await self.sio.disconnect()
            print("👋 Disconnected")

    async def wait(self):
        """Keep connection alive"""
        await self.sio.wait()

def get_default_markets():
    """Helper function to access global market addresses"""
    return MARKET_ADDRESSES

async def main():
    """Main execution function"""
    global MARKET_ADDRESSES
    private_key = os.getenv('PRIVATE_KEY')
    print("=" * 50)
    print("Limitless Exchange WebSocket Client")
    print("=" * 50)
    client = LimitlessWebSocket(private_key=private_key)
    await client.connect()
    if MARKET_ADDRESSES:
        await client.subscribe_markets(MARKET_ADDRESSES)
    else:
        print("⚠️ No market addresses configured")
        return
    print("📡 Listening for events... Press Ctrl+C to stop")
    await client.wait()

if __name__ == "__main__":
    asyncio.run(main())
