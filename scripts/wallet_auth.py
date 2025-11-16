import os
import re
import requests
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct

API_URL = "https://api.limitless.exchange"

def banner(msg: str):
    print(f"[LLMM] {msg}")

def get_signing_message():
    """Fetch signing message (nonce included)."""
    r = requests.get(f"{API_URL}/auth/signing-message", timeout=15)
    r.raise_for_status()
    try:
        return r.json()
    except ValueError:
        return r.text

def extract_nonce(message: str) -> str:
    m = re.search(r"Nonce:\s*(0x[0-9a-fA-F]+)", message)
    if not m:
        raise RuntimeError("Nonce not found in signing message")
    return m.group(1)

def sign_text(text: str, private_key: str):
    acct = Account.from_key(private_key)
    msg = encode_defunct(text=text)
    signed = Account.sign_message(msg, private_key)
    return acct.address, "0x" + signed.signature.hex()

def try_login(account: str, signing_message: str, signature: str, mode: str):
    """Attempt login with given header values."""
    url = f"{API_URL}/auth/login"
    headers = {
        "x-account": account,
        "x-signing-message": signing_message,
        "x-signature": signature,
    }
    body = {"client": "eoa"}
    banner(f"Trying login mode={mode}")
    r = requests.post(url, headers=headers, json=body, timeout=30)
    banner(f"Login status: {r.status_code}")
    banner(f"Response: {r.text}")
    return r.status_code, r.text

def main():
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("PRIVATE_KEY missing in .env")

    # Step 1: Get signing message
    message = get_signing_message()
    banner(f"Signing message:\n{message}")

    # Step 2a: Nonce-only flow
    nonce = extract_nonce(message)
    acct, sig_nonce = sign_text(nonce, private_key)
    try_login(acct, nonce, sig_nonce, mode="nonce-only")

    # Step 2b: Full-message flow (hex header)
    acct2, sig_full = sign_text(message, private_key)
    hex_message = message.encode("utf-8").hex()
    try_login(acct2, hex_message, sig_full, mode="full-message-hex")

if __name__ == "__main__":
    main()
