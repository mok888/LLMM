import requests
import json
import argparse
import time

API_URL = "https://api.limitless.exchange/markets/active"

def list_active_markets(page=1, limit=50, retries=3):
    """List all active markets via REST /markets/active."""
    params = {"page": str(page), "limit": str(limit), "sortBy": "newest"}
    print(f"[LLMM] Listing active markets: {API_URL} {params}")
    for attempt in range(retries):
        try:
            r = requests.get(API_URL, params=params, timeout=30)
            if r.status_code == 200:
                data = r.json()
                markets = data.get("data", [])
                if not markets:
                    print("[LLMM] No markets found.")
                    return []
                print(f"[LLMM] Retrieved {len(markets)} markets:")
                for m in markets:
                    print(json.dumps(m, indent=2))
                return markets
            else:
                print(f"[LLMM] Listing failed: {r.status_code} {r.text}")
        except requests.exceptions.ReadTimeout:
            wait = 2 ** attempt
            print(f"[LLMM] Timeout on attempt {attempt+1}, retrying in {wait}s...")
            time.sleep(wait)
        except Exception as e:
            print("[LLMM] Listing ERROR:", e)
            time.sleep(2)
    return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--limit", type=int, default=50, help="Number of markets per page")
    args = parser.parse_args()

    list_active_markets(page=args.page, limit=args.limit)

if __name__ == "__main__":
    main()
