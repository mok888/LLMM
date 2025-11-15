from core.limitless_client import LimitlessApiClient

def main():
    client = LimitlessApiClient()

    # Account info
    info = client.get_account_info()
    print("[LLMM] Account details:")
    print(f"  Address: {info['address']}")
    print(f"  Chain ID: {info['chain_id']}")
    print(f"  Current Block: {info['block_number']}")
    print(f"  RPC URL: {info['rpc_url']}")

    # Current positions
    positions = client.get_positions()
    print("\n[LLMM] Current positions:")
    if not positions:
        print("  No open positions.")
    else:
        for p in positions:
            market = p.get("market", {}).get("title")
            side = p.get("side")
            size = p.get("size")
            pnl = p.get("pnl")
            print(f"  {market} | Side: {side} | Size: {size} | PnL: {pnl}")

if __name__ == "__main__":
    main()
