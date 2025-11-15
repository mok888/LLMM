def get_positions(self, address=None):
    """
    Attempt to fetch positions for a given wallet address.
    NOTE: This endpoint may not exist in the public API.
    """
    addr = address or self.account.address
    url = f"{self.api_url}/positions/{addr}"
    resp = requests.get(url)

    if resp.status_code == 404:
        print(f"[LLMM] Positions endpoint not found for {addr}.")
        return []

    resp.raise_for_status()
    return resp.json().get("data", [])
