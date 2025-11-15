import asyncio
from core.logging_utils import ws_buffer
async def run_ws_client(session_state):
    while True:
        ws_buffer.append("[WS_CLIENT] ping ok")
        if len(ws_buffer) > 500:
            ws_buffer.pop(0)
        await asyncio.sleep(5)
