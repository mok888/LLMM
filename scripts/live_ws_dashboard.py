import os
import asyncio
import curses
import json
from socket_subs import LimitlessWebSocket

REFRESH_INTERVAL = 1  # seconds

async def ws_listener(client, queue):
    """Listen for WebSocket messages and push them into a queue."""
    while True:
        msg = await client.recv()
        try:
            data = json.loads(msg)
            await queue.put(data)
        except Exception as e:
            print("[LLMM] Failed to parse message:", e)

async def draw_dashboard(stdscr, queue):
    """Render the cockpit dashboard in the terminal."""
    curses.curs_set(0)
    stdscr.nodelay(True)

    state = {"account": {}, "positions": [], "markets": {}}

    while True:
        # Drain queue
        while not queue.empty():
            data = await queue.get()
            channel = data.get("channel")
            if channel == "account":
                state["account"] = data
            elif channel == "positions":
                state["positions"] = data.get("positions", [])
            elif channel == "markets":
                market_id = data.get("marketId")
                state["markets"][market_id] = data

        stdscr.clear()
        stdscr.addstr(0, 0, "[LLMM] FULLY WEBSOCKET COCKPIT DASHBOARD")

        # --- Account Info ---
        acct = state["account"]
        stdscr.addstr(2, 0, "[Account]")
        stdscr.addstr(3, 2, f"Address: {acct.get('address','-')}")
        stdscr.addstr(4, 2, f"Balance: {acct.get('balance','-')}")

        # --- Positions ---
        stdscr.addstr(6, 0, "[Positions]")
        if not state["positions"]:
            stdscr.addstr(7, 2, "No open positions.")
        else:
            for i, p in enumerate(state["positions"], start=7):
                stdscr.addstr(i, 2,
                    f"{p.get('market')} | Side: {p.get('side')} | Size: {p.get('size')} | PnL: {p.get('pnl')}")

        # --- Markets ---
        stdscr.addstr(12, 0, "[Markets]")
        for i, (mid, m) in enumerate(state["markets"].items(), start=13):
            stdscr.addstr(i, 2,
                f"{m.get('title')} | Prices: {m.get('prices')} | Exp: {m.get('expirationDate')}")

        stdscr.refresh()
        await asyncio.sleep(REFRESH_INTERVAL)

async def main():
    private_key = os.getenv("PRIVATE_KEY")
    client = LimitlessWebSocket(private_key=private_key)
    await client.connect()

    # Subscribe to feeds
    await client.subscribe_account()
    await client.subscribe_positions()
    await client.subscribe_markets(["0x1234...", "0x5678..."])  # replace with real market IDs

    queue = asyncio.Queue()

    # Run listener + dashboard concurrently
    await asyncio.gather(
        ws_listener(client, queue),
        curses.wrapper(lambda stdscr: asyncio.run(draw_dashboard(stdscr, queue)))
    )

if __name__ == "__main__":
    asyncio.run(main())
