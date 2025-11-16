import os
import re
import requests
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct

API_URL = "https://api.limitless.exchange"

def banner(msg): print(f"[LLMM] {msg}")

def get_signing_message():
    r = requests.get(f"{API_URL}/auth/signing-message", timeout=15)
    r.raise_for_status()
    return r.text

def extract_nonce(message):
    m = re.search(r"Nonce:\s*(0x[0-9a-fA-F]+)", message)
    if not m:
        raise RuntimeError("Nonce not found in signing message")
    return m.group(1)

def sign_text(text, pk):
    acct = Account.from_key(pk)
    msg = encode_defunct(text=text)
    signed = Account.sign_message(msg, pk)
    return acct.address, "0x" + signed.signature.hex()

def main():
    load_dotenv()
    pk = os.getenv("PRIVATE_KEY")
    if not pk:
        raise RuntimeError("PRIVATE_KEY missing in .env")

    # Step 1: Fetch signing message
    message = get_signing_message()
    banner(f"Signing message:\n{message}")

    # Step 2: Extract nonce
    nonce = extract_nonce(message)

    # Step 3: Sign the nonce (try this flow first)
    acct, sig = sign_text(nonce, pk)
    banner(f"Signed nonce with account: {acct}")

    # Step 4: Login
    headers = {
        "x-account": acct,
        "x-signing-message": nonce,
        "x-signature": sig,
        "Content-Type": "application/json"
    }
    body = {"client": "eoa"}
    s = requests.Session()
    r = s.post(f"{API_URL}/auth/login", headers=headers, json=body, timeout=30)
    banner(f"Login status: {r.status_code}")
    banner(f"Login response: {r.text}")

    # Step 5: Verify auth with same session
    r2 = s.get(f"{API_URL}/auth/verify-auth", timeout=15)
    banner(f"Verify status: {r2.status_code}")
    banner(f"Verify response: {r2.text}")

if __name__ == "__main__":
    main()
