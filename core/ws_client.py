import asyncio
import json
import websockets
from core.logging_utils import ws_buffer

LIMITLESS_WS = "wss://api.limitless.exchange/ws"

async def run_ws_client(session_state):
    async with websockets.connect(LIMITLESS_WS) as ws:
        # Subscribe to multiple markets
        markets = ["BTC-YESNO", "ETH-YESNO", "SOL-YESNO"]
        for m in markets:
            await ws.send(json.dumps({
                "type": "subscribe",
                "channel": "markets",
                "market": m
            }))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            market = data.get("market")
            price = data.get("price")
            volume = data.get("volume")

            if market and price:
                trade_str = f"{market} price={price} vol={volume}"
                session_state.setdefault("trades", []).append(trade_str)
                ws_buffer.append(trade_str)

                if len(ws_buffer) > 500:
                    ws_buffer.pop(0)
