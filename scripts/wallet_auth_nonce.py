import os, re, requests
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct

API_URL = "https://api.limitless.exchange"

def get_signing_message():
    r = requests.get(f"{API_URL}/auth/signing-message", timeout=15)
    r.raise_for_status()
    return r.text

def extract_nonce(message):
    m = re.search(r"Nonce:\s*(0x[0-9a-fA-F]+)", message)
    if not m:
        raise RuntimeError("Nonce not found")
    return m.group(1)

def main():
    load_dotenv()
    pk = os.getenv("PRIVATE_KEY")
    if not pk:
        raise RuntimeError("PRIVATE_KEY missing in .env")

    message = get_signing_message()
    nonce = extract_nonce(message)

    acct = Account.from_key(pk)
    signed = Account.sign_message(encode_defunct(text=nonce), pk)

    headers = {
        "x-account": acct.address,
        "x-signing-message": nonce,
        "x-signature": "0x" + signed.signature.hex(),
    }
    body = {"client": "eoa"}
    r = requests.post(f"{API_URL}/auth/login", headers=headers, json=body, timeout=30)
    print("Login status:", r.status_code)
    print("Response:", r.text)

if __name__ == "__main__":
    main()
