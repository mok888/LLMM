import os
import requests
from eth_account import Account
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "https://api.limitless.exchange")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
BASE_RPC = os.getenv("BASE_RPC")
BASE_CHAIN_ID = int(os.getenv("BASE_CHAIN_ID"))

def main():
    if not PRIVATE_KEY:
        raise RuntimeError("PRIVATE_KEY not set in .env")

    # Wallet setup
    acct = Account.from_key(PRIVATE_KEY)
    print(f"[LLMM] Wallet address: {acct.address}")

    # Web3 setup
    w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    print(f"[LLMM] Connected to chain {BASE_CHAIN_ID}, block {w3.eth.block_number}")

    # Correct REST call
    resp = requests.get(f"{API_URL}/markets/active?page=1&limit=10&sortBy=newest")
    if resp.status_code == 200:
        markets = resp.json()
        print("[LLMM] Markets response:")
        for m in markets.get("data", [])[:5]:
            print(f"  {m}")
    else:
        print(f"[LLMM] Error fetching markets: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    main()
