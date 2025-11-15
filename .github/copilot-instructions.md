## Quick context — what this repo is

LLMM is a small, config-driven Python operator cockpit for interacting with Limitless-style prediction markets. Key runtime pieces live under `core/` and the interactive entrypoints are in `runners/` and `scripts/`.

## High-level architecture (what to know first)

- `core/limitless_client.py` — REST + web3 client that requires a `PRIVATE_KEY` in the environment. Used by scripts (e.g., `scripts/pull_top_volume.py`) to fetch markets and positions.
- `core/ws_client.py` — lightweight websocket consumer; subscribes to markets and writes human-readable strings into the shared `session_state` and `core/logging_utils.py` buffers.
- `core/market_manager_async.py` — background async task runner (currently a sleep loop placeholder) intended to manage periodic market polling/logic.
- `core/session_state.py` — single shared mutable dictionary (global) used for cross-task communication: stores `markets`, `trades`, `assets`.
- `core/dashboard.py` and `scripts/live_ws_dashboard.py` — two dashboard renderers. `core/dashboard.py` returns render rows used by the simple textual dashboard in `runners/runner.py`. `scripts/live_ws_dashboard.py` contains a full curses-based cockpit UI.
- `runners/runner.py` — orchestrator: authenticates (`core/auth.py`), prints startup banners, starts `run_market_manager` and `run_ws_client` as asyncio tasks, and renders the dashboard loop.
- `config/settings.yaml` — small config (mode, asset list). Default mode is `cockpit` in config; `runner.py` will accept a command-line override (`python runners/runner.py dashboard`).

## Key conventions and patterns

- Global shared state: cross-component comms use a single mutable `session_state` dict from `core/session_state.py`. Mutating/reading this dict is the main inter-task contract.
- Simple in-repo logging buffers: `core/logging_utils.py` exposes `ws_buffer` and `trade_buffer` and a `banner()` helper. Code appends short messages to these lists for in-memory history.
- Environment-first secrets: `core/limitless_client.py` will raise if `PRIVATE_KEY` is not present. Other env vars: `API_URL`, `WS_BASE_URL`, `BASE_RPC`, `BASE_CHAIN_ID`, `WALLET_ADDRESS` (used by `core/auth.py`).
- Async tasks + curses: orchestration relies on `asyncio.create_task(...)` + an async main loop. The curses UI runs on top of `asyncio` via `curses.wrapper` in several scripts.

## Run / developer workflows (concrete commands)

- Setup (recommended in PowerShell / WSL):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Environment variables (minimum):
  - `PRIVATE_KEY` — required by `LimitlessApiClient`.
  - `API_URL`, `WS_BASE_URL`, `BASE_RPC`, `BASE_CHAIN_ID` — optional overrides.

- Run the textual dashboard orchestrator (non-curses):

```powershell
python runners/runner.py dashboard
```

- Run the curses cockpit (Unix-like terminal recommended):

```powershell
python runners/runner.py cockpit
```

Note: `requirements.txt` marks `curses` as excluded on Windows (`curses; sys_platform != "win32"`). On Windows use WSL or install a compatible package (for example `windows-curses`) to run the curses cockpit UI.

## Integration points / external dependencies

- REST: `core/limitless_client.py` uses `requests` against `API_URL`.
- Blockchain: `eth-account` + `web3` — the client opens a web3 provider to report block number and uses `PRIVATE_KEY` to derive the wallet address.
- WebSockets: `websockets` package (connection URL via `WS_BASE_URL`) — feeds are parsed and appended into `session_state`.

## What to look for when editing or extending

- If you change the data shape in `session_state`, update all readers/writers (`ws_client.py`, `dashboard.py`, `market_manager_async.py`, `runners/runner.py`) — there is no schema enforcement.
- Keep REST and WS clients separate: `limitless_client.py` is synchronous (requests + web3); `ws_client.py` is async. If you need to call REST from async code, consider running blocking calls in an executor or refactor to an async HTTP client.
- Dashboard showcases are intentionally minimal: `core/dashboard.py` returns `render_dashboard_rows(session_state)` and the runner prints them. Use that pattern for testable rendering logic (pure function that returns rows).

## Small examples to copy/paste

- Create client and fetch top markets (used by `scripts/pull_top_volume.py`):

```python
from core.limitless_client import LimitlessApiClient
client = LimitlessApiClient()
markets = client.get_active_markets(page=1, limit=10, sort="volume")
```

- Append a trade into global state (pattern used in `core/ws_client.py`):

```python
from core.session_state import session_state
session_state.setdefault("trades", []).append("BTC-YESNO price=0.12 vol=100")
```

## Finish & feedback

If anything in this file is unclear, tell me which sections you want expanded (examples, env var matrix, or a runbook for Windows). I can iterate quickly.
