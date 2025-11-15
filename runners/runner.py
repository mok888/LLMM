import asyncio, curses, yaml, sys
from core.session_state import session_state
from core.auth import login_wallet
from core.market_manager_async import run_market_manager
from core.ws_client import run_ws_client
from core.dashboard import render_dashboard_rows
from core.logging_utils import ws_buffer, trade_buffer, banner
from core.banner import startup_banner

async def run_dashboard():
    wallet_id = await login_wallet(session_state)
    startup_banner("dashboard", wallet_id)
    banner("MARKET_MANAGER", status="STARTED")
    asyncio.create_task(run_market_manager(session_state))
    banner("WS_CLIENT", status="CONNECTED")
    asyncio.create_task(run_ws_client(session_state))
    while True:
        rows = render_dashboard_rows(session_state)
        print("\033c")
        print("=== Dashboard ===")
        for row in rows:
            print(row)
        await asyncio.sleep(2)

async def cockpit_main(stdscr):
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()
    top = curses.newwin(h//2, w, 0, 0)
    bottom_left  = curses.newwin(h//2, w//2, h//2, 0)
    bottom_right = curses.newwin(h//2, w//2, h//2, w//2)
    wallet_id = await login_wallet(session_state)
    startup_banner("cockpit", wallet_id)
    banner("MARKET_MANAGER", status="STARTED")
    asyncio.create_task(run_market_manager(session_state))
    banner("WS_CLIENT", status="CONNECTED")
    asyncio.create_task(run_ws_client(session_state))
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    with open("config/settings.yaml") as f:
        cfg = yaml.safe_load(f)
    mode = cfg.get("mode", "dashboard")
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    if mode == "dashboard":
        asyncio.run(run_dashboard())
    else:
        curses.wrapper(lambda stdscr: asyncio.run(cockpit_main(stdscr)))
