# Trader-Vader

Chat-driven Alpaca paper trading. You tell Claude to place a trade; Claude
commits an order file; GitHub Actions executes it against Alpaca and writes the
result back.

## One-time setup

Repo secrets required at `Settings → Secrets and variables → Actions`:

- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`

The workflow uses the paper endpoint (`https://paper-api.alpaca.markets/v2`).
Override with `ALPACA_BASE_URL` in the workflow env if you ever point at live.

## Order file schema

Drop a file at `orders/<client_order_id>.json`:

```json
{
  "symbol": "MSFT",
  "qty": "5",
  "side": "buy",
  "type": "market",
  "time_in_force": "day"
}
```

Fields pass through to Alpaca `POST /v2/orders`. `type` defaults to `market`
and `time_in_force` to `day`. The filename stem becomes the Alpaca
`client_order_id`, so Alpaca rejects duplicates if the same file is ever
re-submitted.

## How the loop works

1. A push that touches `orders/*.json` triggers `.github/workflows/execute-orders.yml`.
2. The workflow runs `execute_orders.py`, which submits any order file without a matching `orders/results/<stem>.json` and writes the Alpaca response to that path.
3. The workflow commits the result files back with `[skip ci]` (and the `orders/results/` path does not match the trigger glob, so it does not recurse).

Re-running the workflow without new orders is a no-op. Orders submitted outside
market hours stay `accepted` until the next open.
