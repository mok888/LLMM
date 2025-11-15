import os
import asyncio
from dotenv import load_dotenv
from limitless_sdk import LimitlessClient
from core.logging_utils import ws_buffer

load_dotenv()

async def run_ws_client(session_state):
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("PRIVATE_KEY not set in .env")

    # Only pass private_key — no base_rpc
    client = LimitlessClient(private_key=private_key)

    await client.login()

    async with client.ws() as ws:
        for m in ["BTC-YESNO", "ETH-YESNO", "SOL-YESNO"]:
            await ws.subscribe("markets", market=m)

        async for event in ws.listen():
            trade_str = f"{event['market']} price={event['price']} vol={event['volume']}"
            session_state.setdefault("trades", []).append(trade_str)
            ws_buffer.append(trade_str)
            if len(ws_buffer) > 500:
                ws_buffer.pop(0)
