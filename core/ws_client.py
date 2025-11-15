import os
import asyncio
from dotenv import load_dotenv
from limitless_sdk import LimitlessClient
from core.logging_utils import ws_buffer

# Load environment variables
load_dotenv()

async def run_ws_client(session_state):
    private_key = os.getenv("PRIVATE_KEY")
    base_rpc = os.getenv("BASE_RPC")

    if not private_key:
        raise RuntimeError("PRIVATE_KEY not set in .env")

    # Initialize Limitless client with wallet key and Base RPC
    client = LimitlessClient(private_key=private_key, base_rpc=base_rpc)

    # Authenticate before using WebSocket
    await client.login()

    async with client.ws() as ws:
        # Subscribe to markets channel
        for m in ["BTC-YESNO", "ETH-YESNO", "SOL-YESNO"]:
            await ws.subscribe("markets", market=m)

        async for event in ws.listen():
            trade_str = f"{event['market']} price={event['price']} vol={event['volume']}"
            session_state.setdefault("trades", []).append(trade_str)
            ws_buffer.append(trade_str)

            if len(ws_buffer) > 500:
                ws_buffer.pop(0)
