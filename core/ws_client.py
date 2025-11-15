# NEW (correct)
import asyncio
from limitless_sdk import LimitlessClient
from core.logging_utils import ws_buffer

async def run_ws_client(session_state):
    # Create client (unauthenticated for public market data)
    client = LimitlessClient()

    # Connect to WebSocket
    async with client.ws() as ws:
        # Subscribe to multiple markets
        for m in ["BTC-YESNO", "ETH-YESNO", "SOL-YESNO"]:
            await ws.subscribe_market(m)

        async for event in ws.listen():
            trade_str = f"{event.market} price={event.price} vol={event.volume}"
            session_state.setdefault("trades", []).append(trade_str)
            ws_buffer.append(trade_str)

            if len(ws_buffer) > 500:
                ws_buffer.pop(0)
