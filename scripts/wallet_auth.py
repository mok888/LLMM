import os
import re
import json
import time
import requests
from typing import Optional, Dict
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct

API_URL = "https://api.limitless.exchange"
SESSION_PATH = ".session.json"

# -------------------------------
# Operator banners
# -------------------------------

def banner(msg: str) -> None:
    print(f"[LLMM] {msg}")

# -------------------------------
# Cookie persistence
# -------------------------------

def save_cookie(session: requests.Session) -> None:
    cookies = session.cookies.get_dict()
    if not cookies:
        banner("No cookies to save.")
        return
    with open(SESSION_PATH, "w") as f:
        json.dump({"cookies": cookies}, f)
    banner(f"Session cookies saved to {SESSION_PATH}")

def load_cookie() -> Optional[Dict[str, str]]:
    if not os.path.exists(SESSION_PATH):
        return None
    try:
        with open(SESSION_PATH, "r") as f:
            data = json.load(f)
            return data.get("cookies")
    except Exception as e:
        banner(f"Failed to load session cookies: {e}")
        return None

def session_with_cookie(cookies: Optional[Dict[str, str]]) -> requests.Session:
    s = requests.Session()
    if cookies:
        for k, v in cookies.items():
            s.cookies.set(k, v, domain="api.limitless.exchange")
        banner("Session cookie loaded into requests.Session")
    return s

# -------------------------------
# Core handshake
# -------------------------------

def get_signing_message(timeout: int = 15, retries: int = 3) -> str:
    url = f"{API_URL}/auth/signing-message"
    backoff = 1
    for attempt in range(1, retries + 1):
        try:
            banner(f"Fetching signing message (attempt {attempt})")
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            try:
                return r.json()  # some servers might return JSON string
            except ValueError:
                return r.text     # most likely plain text
        except requests.RequestException as e:
            banner(f"Signing message fetch failed: {e}; retrying in {backoff}s")
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError("Failed to obtain signing message after retries.")

def extract_nonce(message: str) -> str:
    m = re.search(r"Nonce:\s*(0x[0-9a-fA-F]+)", message)
    if not m:
        raise RuntimeError("Nonce not found in signing message.")
    return m.group(1)

def sign_message(message: str, private_key: str) -> Dict[str, str]:
    acct = Account.from_key(private_key)
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key)
    banner(f"Signed message with account: {acct.address}")
    return {
        "account": acct.address,
        "signature": "0x" + signed.signature.hex().lstrip("0x")  # ensure 0x prefix
    }

def login_session(account: str, message: str, signature: str,
                  timeout: int = 30, retries: int = 2) -> requests.Session:
    url = f"{API_URL}/auth/login"
    nonce = extract_nonce(message)

    headers = {
        "x-account": account,
        "x-signing-message": nonce,      # server expects nonce in header
        "x-signature": signature,        # signature of FULL message
    }
    body = {"client": "eoa"}            # adjust if API requires other fields

    s = requests.Session()
    backoff = 1
    for attempt in range(1, retries + 1):
        try:
            banner(f"Login handshake (attempt {attempt})")
            r = s.post(url, headers=headers, json=body, timeout=timeout)
            banner(f"Login status: {r.status_code}")
            banner(f"Login response: {r.text}")
            if r.status_code == 200:
                banner("Login successful; session cookie set.")
                return s
            elif r.status_code == 401:
                raise RuntimeError("Unauthorized: signature or header mismatch.")
            else:
                raise RuntimeError(f"Unexpected login status: {r.status_code}")
        except requests.RequestException as e:
            banner(f"Login request error: {e}; retrying in {backoff}s")
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError("Login failed after retries.")

def verify_auth(session: requests.Session, timeout: int = 15) -> bool:
    url = f"{API_URL}/auth/verify-auth"
    try:
        r = session.get(url, timeout=timeout)
        banner(f"Verify status: {r.status_code}")
        banner(f"Verify response: {r.text}")
        return r.status_code == 200
    except requests.RequestException as e:
        banner(f"Verify request error: {e}")
        return False

# -------------------------------
# Public entrypoint
# -------------------------------

def get_session(force_relogin: bool = False) -> requests.Session:
    """
    Returns an authenticated session.
    - Loads cookie if present and valid.
    - Otherwise performs full handshake and persists cookie.
    """
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("PRIVATE_KEY missing in .env")

    # Try existing cookie
    if not force_relogin:
        cookies = load_cookie()
        if cookies:
            s = session_with_cookie(cookies)
            banner("Verifying existing session...")
            if verify_auth(s):
                banner("Existing session is valid.")
                return s
            else:
                banner("Existing session invalid; performing re-login.")

    # Fresh handshake
    message = get_signing_message()
    signed = sign_message(message, private_key)
    s = login_session(signed["account"], message, signed["signature"])

    # Persist cookie and verify
    save_cookie(s)
    banner("Verifying new session...")
    if not verify_auth(s):
        banner("Warning: verify-auth did not return 200; session may be gated.")
    return s

# -------------------------------
# Optional demo: list markets
# -------------------------------

def list_markets(session: requests.Session, page: int = 1, limit: int = 20, timeout: int = 30) -> dict:
    url = f"{API_URL}/markets/active"
    params = {"page": str(page), "limit": str(limit), "sortBy": "newest"}
    try:
        banner(f"Listing markets: {params}")
        r = session.get(url, params=params, timeout=timeout)
        banner(f"Markets status: {r.status_code}")
        snippet = r.text[:500]
        banner(f"Markets response snippet: {snippet} ...")
        try:
            return r.json()
        except ValueError:
            return {"raw": r.text}
    except requests.RequestException as e:
        banner(f"Markets request error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # CLI: handshake and verify, then attempt market listing (optional)
    import argparse
    parser = argparse.ArgumentParser(description="Wallet signing and auth handshake")
    parser.add_argument("--force-relogin", action="store_true", help="Ignore saved session and re-login")
    parser.add_argument("--list-markets", action="store_true", help="List active markets after auth")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    sess = get_session(force_relogin=args.force_relogin)

    if args.list_markets:
        data = list_markets(sess, page=args.page, limit=args.limit)
        # Print raw for operator inspection
        print(json.dumps(data, indent=2))
