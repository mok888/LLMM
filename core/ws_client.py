import os
import asyncio
from dotenv import load_dotenv
from limitless_sdk import LimitlessClient
from core.logging_utils import ws_buffer

# Load environment variables from .env
load_dotenv()

async def run_ws_client(session_state):
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("WALLET_PRIVATE_KEY not set in .env")

    # Initialize client with wallet private key
    client = LimitlessClient(private_key=private_key)

    # Authenticate before using WebSocket
    await client.login()

    async with client.ws() as ws:
        # Subscribe to markets channel
        await ws.subscribe("markets", market="BTC-YESNO")
        await ws.subscribe("markets", market="ETH-YESNO")
        await ws.subscribe("markets", market="SOL-YESNO")

        while True:
            event = await ws.recv()   # receive one event (dict)
            # Build trade string from event payload
            trade_str = f"{event['market']} price={event['price']} vol={event['volume']}"
            session_state.setdefault("trades", []).append(trade_str)
            ws_buffer.append(trade_str)

            # Cap buffer size
            if len(ws_buffer) > 500:
                ws_buffer.pop(0)
