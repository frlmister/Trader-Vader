# Trader-Vader

Alpaca paper-trading experiments.

## Testing the connection

```bash
export ALPACA_API_KEY=your_key
export ALPACA_API_SECRET=your_secret
python3 test_alpaca_buy_apple.py
```

The script hits `/v2/account` to verify credentials, then submits a day market
order to buy 1 share of AAPL against the paper endpoint
(`https://paper-api.alpaca.markets`).

Orders submitted outside US market hours sit in `accepted` state and fill at the
next open.
