import os
import requests
from eth_account import Account
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "https://api.limitless.exchange")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
BASE_RPC = os.getenv("BASE_RPC", "https://mainnet.base.org")
BASE_CHAIN_ID = int(os.getenv("BASE_CHAIN_ID", "8453"))

class LimitlessApiClient:
    def __init__(self, api_url=API_URL, private_key=PRIVATE_KEY, rpc_url=BASE_RPC, chain_id=BASE_CHAIN_ID):
        if not private_key:
            raise RuntimeError("PRIVATE_KEY not set in .env")

        self.api_url = api_url
        self.account = Account.from_key(private_key)
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain_id = chain_id

        print(f"[LLMM] Wallet address: {self.account.address}")
        print(f"[LLMM] Connected to chain {self.chain_id}, block {self.web3.eth.block_number}")

    # === Market Endpoints ===
    def get_active_markets(self, page=1, limit=10, sort="newest"):
        url = f"{self.api_url}/markets/active?page={page}&limit={limit}&sortBy={sort}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()["data"]

    def get_market(self, market_id: int):
        url = f"{self.api_url}/markets/{market_id}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    # === Positions ===
    def get_positions(self, address=None):
        addr = address or self.account.address
        url = f"{self.api_url}/positions/{addr}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()["data"]

    # === Orders (simplified placeholder) ===
    def place_order(self, market_id: int, outcome: str, size: int, price: float):
        """
        Example placeholder for placing an order.
        In practice, Limitless requires signed payloads and possibly on-chain tx.
        """
        payload = {
            "marketId": market_id,
            "outcome": outcome,  # "yes" or "no"
            "size": size,
            "price": price,
            "trader": self.account.address,
        }
        url = f"{self.api_url}/orders"
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
def get_hourly_markets(self, page=1, limit=10, sort="newest"):
    url = f"{self.api_url}/markets/active?page={page}&limit={limit}&sortBy={sort}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    # Filter for hourly events
    return [m for m in data if "Hourly" in m.get("tags", []) or "Hourly" in m.get("categories", [])]
	    def get_hourly_markets(self, page=1, limit=10, sort="newest"):
        """
        Fetch active markets and filter for those tagged as Hourly.
        """
        url = f"{self.api_url}/markets/active?page={page}&limit={limit}&sortBy={sort}"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        # Filter for hourly events
        return [
            m for m in data
            if "Hourly" in m.get("tags", []) or "Hourly" in m.get("categories", [])
        ]