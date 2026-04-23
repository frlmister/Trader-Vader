"""Submit any unprocessed order files in `orders/` to Alpaca.

For each `orders/<stem>.json` without a matching `orders/results/<stem>.json`,
submit it to Alpaca's paper endpoint and write the response to the results
directory. The filename stem is used as the Alpaca `client_order_id`, so a
re-run of the same file is rejected by Alpaca as a duplicate.

Creds come from env vars ALPACA_API_KEY / ALPACA_API_SECRET.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets/v2")
API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")

ORDERS_DIR = Path("orders")
RESULTS_DIR = ORDERS_DIR / "results"


def submit(order: dict) -> tuple[int, dict]:
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(
        f"{BASE_URL}/orders",
        data=json.dumps(order).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return e.code, parsed


def main() -> None:
    if not API_KEY or not API_SECRET:
        sys.exit("Set ALPACA_API_KEY and ALPACA_API_SECRET env vars before running.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    failures = 0
    processed = 0
    for order_path in sorted(ORDERS_DIR.glob("*.json")):
        stem = order_path.stem
        result_path = RESULTS_DIR / f"{stem}.json"
        if result_path.exists():
            print(f"skip {stem}: already has result")
            continue

        spec = json.loads(order_path.read_text())
        spec.setdefault("type", "market")
        spec.setdefault("time_in_force", "day")
        spec["client_order_id"] = stem

        print(f"submit {stem}: {spec['side']} {spec.get('qty', spec.get('notional'))} {spec['symbol']}")
        status, body = submit(spec)
        result_path.write_text(json.dumps({"http_status": status, "response": body}, indent=2))
        processed += 1
        if status >= 400:
            failures += 1
            print(f"  FAIL http={status}: {body}")
        else:
            print(f"  OK id={body.get('id')} status={body.get('status')}")

    print(f"done: processed={processed} failures={failures}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
