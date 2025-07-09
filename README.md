# Binance Futures Trading Bot

This is a simple Python trading bot for Binance Futures Testnet. It allows placing MARKET, LIMIT, STOP_LIMIT, and OCO orders using the Binance API.

## Features

- Connects to Binance Futures Testnet using API key and secret
- Supports multiple order types: MARKET, LIMIT, STOP_LIMIT, OCO
- Logs API requests, order execution results, and errors to `trading_bot.log`
- Includes input validation for order parameters
- Test script `test_trading_bot.py` simulates placing various orders and generates logs

## Setup

1. Install required packages:
```
pip install python-binance
```

2. Run the bot:
```
python trading_bot.py
```

3. Run the test script to simulate orders and generate logs:
```
python test_trading_bot.py
```

## Logging

The bot logs important events such as order placement attempts, responses, and errors to `trading_bot.log` in the current directory.

## Notes

- Use your Binance Futures Testnet API key and secret when running the bot.
- The test script uses dummy API keys and simulates various order types for testing purposes.

## License

This project is provided as-is for educational purposes.
