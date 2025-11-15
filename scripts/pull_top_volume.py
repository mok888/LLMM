from core.limitless_client import LimitlessApiClient

def main():
    client = LimitlessApiClient()
    # Fetch top 10 markets sorted by volume
    markets = client.get_active_markets(page=1, limit=10, sort="volume")

    print("[LLMM] Top 10 markets by volume:")
    for m in markets:
        title = m.get("title")
        volume = m.get("volume")
        expiration = m.get("expirationDate")
        print(f"  {title} | Volume: {volume} | Expiration: {expiration}")

if __name__ == "__main__":
    main()
