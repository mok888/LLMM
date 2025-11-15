def render_dashboard_rows(session_state):
    trades = session_state.get("trades", [])
    return trades[-10:]  # show last 10 trades
