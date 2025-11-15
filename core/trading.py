import requests
from eth_account import Account
from eth_account.messages import encode_structured_data
from core.config import PRIVATE_KEY, LIMITLESS_API

class TradingClient:
    def __init__(self, private_key=PRIVATE_KEY, api_url=LIMITLESS_API):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.api_url = api_url
        self.auth_token = None

    def authenticate(self):
        challenge = requests.get(f"{self.api_url}/auth/challenge").json()
        message = challenge["message"]

        signed = Account.sign_message(
            encode_structured_data(message),
            self.private_key
        )

        resp = requests.post(f"{self.api_url}/auth/verify", json={
            "address": self.account.address,
            "signature": signed.signature.hex()
        })
        self.auth_token = resp.json().get("token")
        return self.auth_token

    def submit_order(self, order_struct):
        typed_data = {
            "types": order_struct["types"],
            "domain": order_struct["domain"],
            "primaryType": "Order",
            "message": order_struct["message"]
        }

        signed = Account.sign_message(
            encode_structured_data(typed_data),
            self.private_key
        )

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        resp = requests.post(f"{self.api_url}/orders", json={
            "order": typed_data,
            "signature": signed.signature.hex()
        }, headers=headers)

        return resp.json()
