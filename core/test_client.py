from core.limitless_client import LimitlessApiClient

def main():
    # Initialize client (loads API_URL, PRIVATE_KEY, RPC from .env)
    client = LimitlessApiClient()

    # Fetch active markets
    markets = client.get_active_markets(limit=5)
    print("[LLMM] Active markets:")
    for m in markets:
        print(f"  {m['title']} | Prices: {m['prices']} | Status: {m['status']}")

if __name__ == "__main__":
    main()
