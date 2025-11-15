import os
async def login_wallet(session_state):
    return os.getenv("WALLET_ADDRESS", "unknown-wallet")
