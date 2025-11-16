import sys
from limitless_auth import get_session

API_URL = "https://api.limitless.exchange"

def get_slugs(session, tickers):
    url = f"{API_URL}/markets/active/slugs"
    params = {"tickers": ",".join(tickers)}
    r = session.get(url, params=params, timeout=30)
    print("[LLMM] Slugs status:", r.status_code)
    print(r.json())

def main():
    session = get_session()
    tickers = sys.argv[1:] or ["BTC", "ETH"]
    get_slugs(session, tickers)

if __name__ == "__main__":
    main()
