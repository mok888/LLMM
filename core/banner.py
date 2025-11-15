def startup_banner(mode: str, wallet: str = None):
    ascii_logo = r"""
 __        ___     _ _       _
 \ \      / / |__ (_) |_ ___| |__   ___
  \ \ /\ / /| '_ \| | __/ __| '_ \ / _ \
   \ V  V / | | | | | || (__| | | |  __/
    \_/\_/  |_| |_|_|\__\___|_| |_|\___|
    LLMM
    """
    print(ascii_logo)
    print(f"Mode: {mode.upper()}")
    if wallet:
        print(f"Wallet authenticated: {wallet}")
    print("========================================")
