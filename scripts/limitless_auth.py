#!/usr/bin/env python3
"""
Limitless Exchange Authentication Script
⚠️ Demo script for educational purposes.
"""

import os
import requests
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct

API_URL = "https://api.limitless.exchange"

def banner(msg): 
    print(f"[LLMM] {msg}")

def get_signing_message():
    """Fetch signing message from API."""
    r = requests.get(f"{API_URL}/auth/signing-message", timeout=15)
    r.raise_for_status()
    return r.text

def sign_message(message: str, private_key: str):
    """Sign the full message string."""
    acct = Account.from_key(private_key)
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key)
    sig_hex = signed.signature.hex()
    if not sig_hex.startswith("0x"):
        sig_hex = "0x" + sig_hex
    return acct.address, sig_hex

def login(account: str, message: str, signature: str):
    """Perform login handshake."""
    hex_message = "0x" + message.encode("utf-8").hex()
    headers = {
        "x-account": account,
        "x-signing-message": hex_message,
        "x-signature": signature,
        "Content-Type": "application/json",
    }
    body = {"client": "eoa"}
    s = requests.Session()
    r = s.post(f"{API_URL}/auth/login", headers=headers, json=body, timeout=30)
    banner(f"Login status: {r.status_code}")
    banner(f"Login response: {r.text}")
    return s, r

def verify_auth(session: requests.Session):
    """Verify session cookie."""
    r = session.get(f"{API_URL}/auth/verify-auth", timeout=15)
    banner(f"Verify status: {r.status_code}")
    banner(f"Verify response: {r.text}")

def get_session():
    """Return an authenticated session object for reuse."""
    load_dotenv()
    pk = os.getenv("PRIVATE_KEY")
    if not pk:
        raise RuntimeError("PRIVATE_KEY missing in .env")

    message = get_signing_message()
    banner(f"Signing message:\n{message}")

    account, signature = sign_message(message, pk)
    banner(f"Signed message with account: {account}")

    session, resp = login(account, message, signature)
    verify_auth(session)
    return session

def main():
    # Run auth flow and return session
    return get_session()

if __name__ == "__main__":
    main()
