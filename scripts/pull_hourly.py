if __name__ == "__main__":
    main()

from core.limitless_client import LimitlessApiClient

def main():
    client = LimitlessApiClient()
    hourly_markets = client.get_hourly_markets(limit=10)

    print("[LLMM] Hourly events:")
    for m in hourly_markets:
        print(f"  {m['title']} | Prices: {m['prices']} | Expiration: {m['expirationDate']}")

if __name__ == "__main__":
    main()
