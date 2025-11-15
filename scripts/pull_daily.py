from core.limitless_client import LimitlessApiClient

def main():
    client = LimitlessApiClient()
    daily_markets = client.get_daily_markets(limit=10)

    print("[LLMM] Daily events:")
    for m in daily_markets:
        title = m.get("title")
        prices = m.get("prices")
        expiration = m.get("expirationDate")
        print(f"  {title} | Prices: {prices} | Expiration: {expiration}")

if __name__ == "__main__":
    main()
