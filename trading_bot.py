import logging
import sys
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager  # type: ignore
from binance.exceptions import BinanceAPIException, BinanceOrderException  # type: ignore


class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self._setup_client()
        self._setup_logger()

    def _setup_client(self):
        self.client = Client(self.api_key, self.api_secret)
        if self.testnet:
            self.client.API_URL = 'https://testnet.binancefuture.com/fapi'

    def _setup_logger(self):
        self.logger = logging.getLogger('BasicBot')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('trading_bot.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.handler = handler  # Save handler for flushing

    def _flush_log(self):
        for handler in self.logger.handlers:
            handler.flush()

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None, stop_limit_price=None):
        """
        Place an order on Binance Futures Testnet.
        :param symbol: trading pair symbol, e.g. 'BTCUSDT'
        :param side: 'BUY' or 'SELL'
        :param order_type: 'MARKET', 'LIMIT', 'STOP_LIMIT', or 'OCO'
        :param quantity: quantity to buy/sell
        :param price: price for LIMIT or STOP_LIMIT orders
        :param stop_price: stop price for STOP_LIMIT or OCO orders
        :param stop_limit_price: limit price for OCO orders
        :return: order response dict or None
        """
        try:
            self.logger.info(f"Placing order: symbol={symbol}, side={side}, type={order_type}, quantity={quantity}, price={price}, stop_price={stop_price}, stop_limit_price={stop_limit_price}")
            self._flush_log()
            if order_type == 'MARKET':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity
                )
            elif order_type == 'LIMIT':
                if price is None:
                    raise ValueError("Price must be specified for LIMIT orders")
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price
                )
            elif order_type == 'STOP_LIMIT':
                if price is None or stop_price is None:
                    raise ValueError("Price and stop_price must be specified for STOP_LIMIT orders")
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='STOP',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price,
                    stopPrice=stop_price
                )
            elif order_type == 'OCO':
                if stop_price is None or stop_limit_price is None or price is None:
                    raise ValueError("Price, stop_price and stop_limit_price must be specified for OCO orders")
                # Binance Futures API does not support OCO directly, so we simulate OCO by placing two orders
                # Here we place a LIMIT order and a STOP_LIMIT order and rely on user to manage cancellation
                limit_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='LIMIT',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price
                )
                stop_limit_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='STOP',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=stop_limit_price,
                    stopPrice=stop_price
                )
                order = {'limit_order': limit_order, 'stop_limit_order': stop_limit_order}
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            self.logger.info(f"Order response: {order}")
            self._flush_log()
            return order
        except (BinanceAPIException, BinanceOrderException, ValueError) as e:
            self.logger.error(f"Error placing order: {e}")
            self._flush_log()
            print(f"Error placing order: {e}")
            return None


def validate_input(symbol, side, order_type, quantity, price, stop_price, stop_limit_price=None):
    valid_sides = ['BUY', 'SELL']
    valid_order_types = ['MARKET', 'LIMIT', 'STOP_LIMIT', 'OCO']

    if not symbol or not isinstance(symbol, str):
        print("Invalid symbol.")
        return False
    if side not in valid_sides:
        print("Invalid side. Must be 'BUY' or 'SELL'.")
        return False
    if order_type not in valid_order_types:
        print("Invalid order type. Must be 'MARKET', 'LIMIT', 'STOP_LIMIT', or 'OCO'.")
        return False
    try:
        quantity = float(quantity)
        if quantity <= 0:
            print("Quantity must be positive.")
            return False
    except ValueError:
        print("Quantity must be a number.")
        return False
    if order_type in ['LIMIT', 'STOP_LIMIT', 'OCO']:
        try:
            price = float(price)
            if price <= 0:
                print("Price must be positive.")
                return False
        except (ValueError, TypeError):
            print("Price must be a number.")
            return False
    if order_type == 'STOP_LIMIT':
        try:
            stop_price = float(stop_price)
            if stop_price <= 0:
                print("Stop price must be positive.")
                return False
        except (ValueError, TypeError):
            print("Stop price must be a number.")
            return False
    if order_type == 'OCO':
        try:
            stop_price = float(stop_price)
            stop_limit_price = float(stop_limit_price)
            if stop_price <= 0 or stop_limit_price <= 0:
                print("Stop price and stop limit price must be positive.")
                return False
        except (ValueError, TypeError):
            print("Stop price and stop limit price must be numbers.")
            return False
    return True


def main():
    print("Welcome to the Binance Futures Testnet Trading Bot")
    api_key = input("Enter your Binance API Key: ").strip()
    api_secret = input("Enter your Binance API Secret: ").strip()

    bot = BasicBot(api_key, api_secret, testnet=True)

    while True:
        print("\nEnter order details:")
        symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
        side = input("Side (BUY/SELL): ").strip().upper()
        order_type = input("Order Type (MARKET/LIMIT/STOP_LIMIT/OCO): ").strip().upper()
        quantity = input("Quantity: ").strip()
        price = None
        stop_price = None
        stop_limit_price = None
        if order_type in ['LIMIT', 'STOP_LIMIT', 'OCO']:
            price = input("Price: ").strip()
        if order_type == 'STOP_LIMIT':
            stop_price = input("Stop Price: ").strip()
        if order_type == 'OCO':
            stop_price = input("Stop Price: ").strip()
            stop_limit_price = input("Stop Limit Price: ").strip()

        if not validate_input(symbol, side, order_type, quantity, price, stop_price, stop_limit_price):
            print("Invalid input. Please try again.")
            continue

        order = bot.place_order(
            symbol,
            side,
            order_type,
            float(quantity),
            float(price) if price else None,
            float(stop_price) if stop_price else None,
            float(stop_limit_price) if stop_limit_price else None
        )
        if order:
            print("Order placed successfully:")
            print(order)
        else:
            print("Failed to place order.")

        cont = input("Place another order? (y/n/restart): ").strip().lower()
        if cont == 'n':
            print("Exiting trading bot.")
            break
        elif cont == 'restart':
            print("Restarting trading bot...")
            main()
            break
        elif cont != 'y':
            print("Invalid input. Exiting trading bot.")
            break


if __name__ == "__main__":
    main()
