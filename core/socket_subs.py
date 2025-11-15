import asyncio, websockets, json, logging
from core.config import LIMITLESS_API, HEARTBEAT_INTERVAL

logging.basicConfig(level=logging.INFO)

class LimitlessWebSocket:
    def __init__(self, uri=f"{LIMITLESS_API}/markets", heartbeat_interval=HEARTBEAT_INTERVAL):
        self.uri = uri
        self.conn = None
        self.heartbeat_interval = heartbeat_interval
        self._stop = False

    async def connect(self):
        while not self._stop:
            try:
                logging.info("[LLMM] Connecting WS …")
                self.conn = await websockets.connect(self.uri, ping_interval=None)
                logging.info("[LLMM] Connected.")
                return
            except Exception as e:
                logging.error(f"[LLMM] WS connect failed: {e}. Retrying in 5s…")
                await asyncio.sleep(5)

    async def heartbeat(self):
        while not self._stop:
            try:
                if self.conn:
                    await self.conn.send(json.dumps({"action": "ping"}))
                    logging.debug("[LLMM] Sent heartbeat ping.")
            except Exception as e:
                logging.warning(f"[LLMM] Heartbeat failed: {e}")
                await self.connect()
            await asyncio.sleep(self.heartbeat_interval)

    async def subscribe_markets(self, market_ids):
        await self.conn.send(json.dumps({
            "action": "subscribe",
            "channel": "markets",
            "ids": market_ids
        }))

    async def subscribe_positions(self):
        await self.conn.send(json.dumps({
            "action": "subscribe",
            "channel": "positions"
        }))

    async def recv(self):
        while not self._stop:
            try:
                return await self.conn.recv()
            except Exception as e:
                logging.error(f"[LLMM] recv failed: {e}. Reconnecting…")
                await self.connect()

    async def close(self):
        self._stop = True
        if self.conn:
            await self.conn.close()
            logging.info("[LLMM] WS closed.")
