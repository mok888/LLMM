ws_buffer = []
trade_buffer = []
def banner(component, status="OK"):
    msg = f"[{component}] {status}"
    print(msg)
    ws_buffer.append(msg)
    if len(ws_buffer) > 500:
        ws_buffer.pop(0)
