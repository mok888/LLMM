import asyncio
import aiohttp

async def test():
    url = "wss://ws.limitless.exchange/socket.io/?EIO=4&transport=websocket"
    headers = {"Origin": "https://limitless.exchange", "User-Agent": "LLMM/1.0"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.ws_connect(url, headers=headers) as ws:
                print("connected")
        except Exception as e:
            print("ws_connect failed:", type(e).__name__, e)

asyncio.run(test())
