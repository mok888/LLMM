import asyncio
from limitless_sdk import LimitlessClient
from core.logging_utils import ws_buffer

async def run_ws_client(session_state):
    async with LimitlessWSClient() as client:
        # Subscribe to multiple markets
        for m in ["BTC-YESNO", "ETH-YESNO", "SOL-YESNO"]:
            await client.subscribe_market(m)

        async for event in client.listen():
            # SDK gives structured events
            trade_str = f"{event.market} price={event.price} vol={event.volume}"
            session_state.setdefault("trades", []).append(trade_str)
            ws_buffer.append(trade_str)

            if len(ws_buffer) > 500:
                ws_buffer.pop(0)
