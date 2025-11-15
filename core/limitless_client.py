class LimitlessApiClient:
    def __init__(self, api_url=API_URL, private_key=PRIVATE_KEY, rpc_url=BASE_RPC, chain_id=BASE_CHAIN_ID):
        # ... your init code ...

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

    def get_positions(self, address=None):
        addr = address or self.account.address
        url = f"{self.api_url}/positions/{addr}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()["data"]

    def get_hourly_markets(self, page=1, limit=10, sort="newest"):
        """
        Fetch active markets and filter for those tagged as Hourly.
        """
        url = f"{self.api_url}/markets/active?page={page}&limit={limit}&sortBy={sort}"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [m for m in data if "Hourly" in m.get("tags", []) or "Hourly" in m.get("categories", [])]
