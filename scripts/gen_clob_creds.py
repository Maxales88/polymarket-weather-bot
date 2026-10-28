"""Generate CLOB API credentials from private key (run once)."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


def main():
    pk = os.getenv("POLYMARKET_PRIVATE_KEY")
    if not pk:
        print("Set POLYMARKET_PRIVATE_KEY in .env first")
        return
    try:
        from py_clob_client.client import ClobClient
    except ImportError:
        print("pip install py-clob-client")
        return
    client = ClobClient(host="https://clob.polymarket.com", key=pk, chain_id=137)
    creds = client.create_or_derive_api_creds()
    print("API_KEY=", creds.api_key)
    print("API_SECRET=", creds.api_secret)
    print("API_PASSPHRASE=", creds.api_passphrase)


if __name__ == "__main__":
    main()
