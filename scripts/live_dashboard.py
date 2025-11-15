import curses
import time
from core.limitless_client import LimitlessApiClient

REFRESH_INTERVAL = 5  # seconds

def draw_dashboard(stdscr, client):
    curses.curs_set(0)  # hide cursor
    stdscr.nodelay(True)

    while True:
        stdscr.clear()

        # --- Account Info ---
        info = client.get_account_info()
        stdscr.addstr(0, 0, "[LLMM] LIVE COCKPIT DASHBOARD")
        stdscr.addstr(2, 0, f"Address: {info['address']}")
        stdscr.addstr(3, 0, f"Chain ID: {info['chain_id']} | Block: {info['block_number']}")

        # --- Current Positions ---
        stdscr.addstr(5, 0, "[Current Positions]")
        try:
            positions = client.get_positions()
            if not positions:
                stdscr.addstr(6, 2, "No open positions.")
            else:
                for i, p in enumerate(positions, start=6):
                    market = p.get("market", {}).get("title")
                    side = p.get("side")
                    size = p.get("size")
                    pnl = p.get("pnl")
                    stdscr.addstr(i, 2, f"{market} | Side: {side} | Size: {size} | PnL: {pnl}")
        except Exception as e:
            stdscr.addstr(6, 2, f"Positions unavailable: {e}")

        # --- Hourly Markets ---
        line = 8 + len(positions or [])
        hourly = client.get_hourly_markets(limit=5)
        stdscr.addstr(line, 0, "[Hourly Markets]")
        if not hourly:
            stdscr.addstr(line+1, 2, "No hourly markets found.")
        else:
            for i, m in enumerate(hourly, start=line+1):
                stdscr.addstr(i, 2, f"{m['title']} | Prices: {m.get('prices')} | Exp: {m.get('expirationDate')}")

        # --- Daily Markets ---
        line = line + len(hourly) + 3
        daily = client.get_daily_markets(limit=5)
        stdscr.addstr(line, 0, "[Daily Markets]")
        if not daily:
            stdscr.addstr(line+1, 2, "No daily markets found.")
        else:
            for i, m in enumerate(daily, start=line+1):
                stdscr.addstr(i, 2, f"{m['title']} | Prices: {m.get('prices')} | Exp: {m.get('expirationDate')}")

        stdscr.refresh()
        time.sleep(REFRESH_INTERVAL)

def main():
    client = LimitlessApiClient()
    curses.wrapper(draw_dashboard, client)

if __name__ == "__main__":
    main()
