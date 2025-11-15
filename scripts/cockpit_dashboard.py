from core.limitless_client import LimitlessApiClient

def main():
    client = LimitlessApiClient()

    # --- Account Info ---
    info = client.get_account_info()
    print("\n[LLMM] ACCOUNT INFO")
    print("=" * 50)
    print(f"Address:       {info['address']}")
    print(f"Chain ID:      {info['chain_id']}")
    print(f"Current Block: {info['block_number']}")
    print(f"RPC URL:       {info['rpc_url']}")

    # --- Current Positions ---
    print("\n[LLMM] CURRENT POSITIONS")
    print("=" * 50)
    try:
        positions = client.get_positions()
        if not positions:
            print("No open positions.")
        else:
            for p in positions:
                market = p.get("market", {}).get("title")
                side = p.get("side")
                size = p.get("size")
                pnl = p.get("pnl")
                print(f"{market} | Side: {side} | Size: {size} | PnL: {pnl}")
    except Exception as e:
        print(f"Positions unavailable: {e}")

    # --- Hourly Markets ---
    print("\n[LLMM] HOURLY MARKETS")
    print("=" * 50)
    hourly = client.get_hourly_markets(limit=10)
    if not hourly:
        print("No hourly markets found.")
    else:
        for m in hourly:
            print(f"{m['title']} | Prices: {m.get('prices')} | Exp: {m.get('expirationDate')}")

    # --- Daily Markets ---
    print("\n[LLMM] DAILY MARKETS")
    print("=" * 50)
    daily = client.get_daily_markets(limit=10)
    if not daily:
        print("No daily markets found.")
    else:
        for m in daily:
            print(f"{m['title']} | Prices: {m.get('prices')} | Exp: {m.get('expirationDate')}")

if __name__ == "__main__":
    main()
