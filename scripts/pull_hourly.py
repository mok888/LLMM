from core.limitless_client import LimitlessApiClient

def main():
    client = LimitlessApiClient()
    hourly_markets = client.get_hourly_markets(limit=10)

    print("[LLMM] Hourly events:")
    for m in hourly_markets:
        title = m.get("title")
        prices = m.get("prices")
        expiration = m.get("expirationDate")
        print(f"  {title} | Prices: {prices} | Expiration: {expiration}")

if __name__ == "__main__":
    main()