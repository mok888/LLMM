import asyncio, curses, json
from core.socket_subs import LimitlessWebSocket
from core.config import MARKET_IDS, REFRESH_INTERVAL

async def ws_listener(client, q):
    while True:
        msg = await client.recv()
        try:
            data = json.loads(msg)
            await q.put(data)
        except Exception as e:
            print("[LLMM] Parse fail:", e)

async def draw(stdscr, q):
    curses.curs_set(0); stdscr.nodelay(True)
    state = {"positions": [], "markets": {}}

    while True:
        while not q.empty():
            d = await q.get()
            ch = d.get("channel")
            if ch == "positions":
                state["positions"] = d.get("positions", [])
            elif ch == "markets":
                mid = d.get("marketId")
                state["markets"][mid] = d

        stdscr.clear()
        stdscr.addstr(0, 0, "[LLMM] WebSocket cockpit")
        stdscr.addstr(2, 0, "[Positions]")
        if not state["positions"]:
            stdscr.addstr(3, 2, "No open positions.")
        else:
            for i, p in enumerate(state["positions"], start=3):
                stdscr.addstr(i, 2, f"{p.get('market')} | {p.get('side')} | {p.get('size')} | PnL {p.get('pnl')}")

        stdscr.addstr(10, 0, "[Markets]")
        for i, (mid, m) in enumerate(state["markets"].items(), start=11):
            stdscr.addstr(i, 2, f"{m.get('title')} | {m.get('prices')} | exp {m.get('expirationDate')}")

        stdscr.refresh()
        await asyncio.sleep(REFRESH_INTERVAL)

async def main():
    client = LimitlessWebSocket()
    await client.connect()
    await client.subscribe_positions()
    if MARKET_IDS:
        await client.subscribe_markets(MARKET_IDS)

    q = asyncio.Queue()
    await asyncio.gather(
        ws_listener(client, q),
        client.heartbeat(),
        curses.wrapper(lambda s: asyncio.run(draw(s, q)))
    )

if __name__ == "__main__":
    asyncio.run(main())
