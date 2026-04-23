"""Smoke-test the Alpaca paper-trading connection by buying 1 share of AAPL.

Usage:
    export ALPACA_API_KEY=...
    export ALPACA_API_SECRET=...
    python3 test_alpaca_buy_apple.py
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets/v2")
API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")


def request(method: str, path: str, body: dict | None = None) -> dict:
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} on {method} {path}: {e.read().decode()}")


def main() -> None:
    if not API_KEY or not API_SECRET:
        sys.exit("Set ALPACA_API_KEY and ALPACA_API_SECRET env vars before running.")

    account = request("GET", "/account")
    print(f"Account {account['account_number']} status={account['status']} "
          f"cash=${account['cash']} buying_power=${account['buying_power']}")

    order = request("POST", "/orders", {
        "symbol": "AAPL",
        "qty": "1",
        "side": "buy",
        "type": "market",
        "time_in_force": "day",
    })
    print(f"Order submitted: id={order['id']} status={order['status']} "
          f"symbol={order['symbol']} qty={order['qty']} side={order['side']}")


if __name__ == "__main__":
    main()
