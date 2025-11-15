from core.limitless_client import LimitlessApiClient

def main():
    client = LimitlessApiClient()

    # --- Account Info ---
    info = client.get_account_info()
    print("\n[LLMM] ACCOUNT INFO")
    print("=" * 40)
    print(f"Address:       {info['address']}")
    print(f"Chain ID:      {info['chain_id']}")
    print(f"Current Block: {info['block_number']}")
    print(f"RPC URL:       {info['rpc_url']}")

    # --- Current Positions ---
    positions = client.get_positions()
    print("\n[LLMM] CURRENT POSITIONS")
    print("=" * 40)
    if not positions:
        print("No open positions.")
    else:
        for p in positions:
            market = p.get("market", {}).get("title")
            side = p.get("side")
            size = p.get("size")
            pnl = p.get("pnl")
            print(f"{market} | Side: {side} | Size: {size} | PnL: {pnl}")

    # --- Hourly Markets ---
    hourly = client.get_hourly_markets(limit=10)
    print("\n[LLMM] HOURLY MARKETS")
    print("=" * 40)
    for m in hourly:
        print(f"{m['title']} | Prices: {m.get('prices')} | Exp: {m.get('expirationDate')}")

    # --- Daily Markets ---
    daily = client.get_daily_markets(limit=10)
    print("\n[LLMM] DAILY MARKETS")
    print("=" * 40)
    for m in daily:
        print(f"{m['title']} | Prices: {m.get('prices')} | Exp: {m.get('expirationDate')}")

    # --- Top Volume Markets ---
    top_volume = client.get_top_volume_markets(top_n=10)
    print("\n[LLMM] TOP 10 MARKETS BY VOLUME")
    print("=" * 40)
    for m in top_volume:
        print(f"{m['title']} | Volume: {m.get('volume')} | Exp: {m.get('expirationDate')}")

if __name__ == "__main__":
    main()
