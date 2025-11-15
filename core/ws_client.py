import os
import asyncio
import json
import websockets
from dotenv import load_dotenv
from core.logging_utils import ws_buffer

load_dotenv()
WS_BASE_URL = os.getenv("WS_BASE_URL", "wss://api.limitless.exchange/markets")

async def run_ws_client(session_state):
    async with websockets.connect(WS_BASE_URL) as ws:
        # Subscribe to markets
        for m in ["BTC-YESNO", "ETH-YESNO", "SOL-YESNO"]:
            await ws.send(json.dumps({
                "type": "subscribe",
                "channel": "markets",
                "market": m
            }))

        while True:
            msg = await ws.recv()
            event = json.loads(msg)

            if event.get("type") == "market":
                trade_str = f"{event['market']} price={event['price']} vol={event['volume']}"
                session_state.setdefault("trades", []).append(trade_str)
                ws_buffer.append(trade_str)

                if len(ws_buffer) > 500:
                    ws_buffer.pop(0)
