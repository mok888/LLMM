#!/usr/bin/env bash
set -euo pipefail

echo "[SETUP] Creating LLMM repo structure..."

# Root folders
mkdir -p core runners config docs scripts

# .gitignore
cat > .gitignore << 'GIT'
__pycache__/
*.pyc
.venv/
.env
GIT

# README.md
cat > README.md << 'README'
# LLMM 🪙

A resilient, config‑driven trading bot designed for binary prediction markets.  
Features cockpit‑style operator control, lifecycle markers, heartbeat monitoring, and split‑screen dashboards for unmistakable clarity in production.
README

# OPERATIONS.md
cat > docs/OPERATIONS.md << 'OPS'
# Operator Playbook — LLMM

See README for overview. This file will contain lifecycle markers, cockpit layout, and cheat sheet.
OPS

# Config placeholder
cat > config/settings.yaml << 'YAML'
mode: cockpit
assets:
  - BTC-YESNO
  - ETH-YESNO
YAML

cat > .env << 'ENV'
WALLET_ADDRESS=0xYOUR_WALLET_ADDRESS
ENV

# Runner skeleton
cat > runners/runner.py << 'RUNNER'
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
RUNNER

# Core stubs
cat > core/session_state.py << 'STATE'
session_state = {"markets": {}, "trades": [], "assets": []}
STATE

cat > core/auth.py << 'AUTH'
import os
async def login_wallet(session_state):
    return os.getenv("WALLET_ADDRESS", "unknown-wallet")
AUTH

cat > core/market_manager_async.py << 'MM'
import asyncio
async def run_market_manager(session_state):
    while True:
        await asyncio.sleep(10)
MM

cat > core/ws_client.py << 'WS'
import asyncio
from core.logging_utils import ws_buffer
async def run_ws_client(session_state):
    while True:
        ws_buffer.append("[WS_CLIENT] ping ok")
        if len(ws_buffer) > 500:
            ws_buffer.pop(0)
        await asyncio.sleep(5)
WS

cat > core/dashboard.py << 'DASH'
def render_dashboard_rows(session_state):
    return ["Asset Spread Countdown", "BTC-YESNO 0.02 00:29:57"]
DASH

cat > core/logging_utils.py << 'LOG'
ws_buffer = []
trade_buffer = []
def banner(component, status="OK"):
    msg = f"[{component}] {status}"
    print(msg)
    ws_buffer.append(msg)
    if len(ws_buffer) > 500:
        ws_buffer.pop(0)
LOG

cat > core/banner.py << 'BNR'
def startup_banner(mode: str, wallet: str = None):
    ascii_logo = r"""
 __        ___     _ _       _
 \ \      / / |__ (_) |_ ___| |__   ___
  \ \ /\ / /| '_ \| | __/ __| '_ \ / _ \
   \ V  V / | | | | | || (__| | | |  __/
    \_/\_/  |_| |_|_|\__\___|_| |_|\___|
    LLMM
    """
    print(ascii_logo)
    print(f"Mode: {mode.upper()}")
    if wallet:
        print(f"Wallet authenticated: {wallet}")
    print("========================================")
BNR

echo "[SETUP] LLMM repo skeleton created."
