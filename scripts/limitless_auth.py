import os
import re
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv

API_URL = "https://api.limitless.exchange"

def get_signing_message():
    """Step 1: Get signing message with nonce."""
    url = f"{API_URL}/auth/signing-message"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    try:
        message = r.json()
    except ValueError:
        message = r.text
    print("[LLMM] Signing message:", message)
    return message

def extract_nonce(message):
    """Extract hex nonce from signing message text."""
    match = re.search(r"Nonce:\s*(0x[0-9a-fA-F]+)", message)
    if not match:
        raise RuntimeError("Nonce not found in signing message")
    return match.group(1)

def sign_message(message, private_key):
    """Step 2: Sign the full message with Ethereum private key."""
    acct = Account.from_key(private_key)
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key)
    print("[LLMM] Signed message with account:", acct.address)
    return acct.address, signed.signature.hex()

def login(account, message, signature):
    """Step 3: Login with headers and body, store session cookie."""
    url = f"{API_URL}/auth/login"

    # Extract nonce for header
    nonce = extract_nonce(message)

    headers = {
        "x-account": account,
        "x-signing-message": nonce,   # only the hex nonce
        "x-signature": signature,
    }
    body = {"client": "eoa"}  # Example body
    session = requests.Session()
    r = session.post(url, headers=headers, json=body, timeout=30)
    print("[LLMM] Login status:", r.status_code)
    print("[LLMM] Response:", r.text)
    return session

def list_markets(session, page=1, limit=10):
    """Step 4: Use session cookie to list markets."""
    url = f"{API_URL}/markets/active"
    params = {"page": str(page), "limit": str(limit), "sortBy": "newest"}
    r = session.get(url, params=params, timeout=30)
    print("[LLMM] Markets status:", r.status_code)
    print("[LLMM] Response:", r.text[:500], "...")
    try:
        return r.json()
    except ValueError:
        return {"raw": r.text}

def main():
    # Load environment variables from .env
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")

    if not private_key:
        raise RuntimeError("PRIVATE_KEY not found in .env file")

    # Step 1: Get signing message
    message = get_signing_message()

    # Step 2: Sign message
    account, signature = sign_message(message, private_key)

    # Step 3: Login
    session = login(account, message, signature)

    # Step 4: List markets
    markets = list_markets(session, page=1, limit=20)
    if "data" in markets:
        for m in markets.get("data", []):
            print(f"id={m['id']} slug={m['slug']} title={m['title']} categories={m.get('categories', [])}")
    else:
        print("[LLMM] Raw markets response:", markets)

if __name__ == "__main__":
    main()
