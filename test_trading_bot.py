import subprocess
import time

def run_trading_bot_test():
    # Start the trading_bot.py script as a subprocess
    proc = subprocess.Popen(
        ['python', 'trading_bot.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    def send_input(input_str):
        proc.stdin.write(input_str + '\\n')
        proc.stdin.flush()
        time.sleep(1)  # Increased delay to ensure input is processed

    # Collect output lines
    output_lines = []

    def read_output():
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            output_lines.append(line)
            print(line, end='')

    # Wait a moment for the process to start and prompt for input
    time.sleep(1)

    # Provide API key and secret (dummy values for testnet)
    send_input('test_api_key')
    send_input('test_api_secret')

    # Test 1: Valid MARKET order
    send_input('BTCUSDT')  # Symbol
    send_input('BUY')      # Side
    send_input('MARKET')   # Order Type
    send_input('0.001')    # Quantity
    # No price inputs for MARKET
    # Continue to place another order? y
    send_input('y')

    # Test 2: Valid LIMIT order
    send_input('BTCUSDT')
    send_input('SELL')
    send_input('LIMIT')
    send_input('0.001')
    send_input('30000')    # Price
    send_input('y')

    # Test 3: Valid STOP_LIMIT order
    send_input('BTCUSDT')
    send_input('BUY')
    send_input('STOP_LIMIT')
    send_input('0.001')
    send_input('31000')    # Price
    send_input('30500')    # Stop Price
    send_input('y')

    # Test 4: Valid OCO order
    send_input('BTCUSDT')
    send_input('SELL')
    send_input('OCO')
    send_input('0.001')
    send_input('32000')    # Price
    send_input('31500')    # Stop Price
    send_input('31000')    # Stop Limit Price
    send_input('y')

    # Test 5: Invalid inputs
    send_input('')         # Invalid symbol
    send_input('BUY')
    send_input('MARKET')
    send_input('0')
    send_input('n')        # Exit after invalid input

    # Test 6: Restart command
    # Restart the bot by running main again
    # This requires a new process, so we skip here

    # Exit the bot
    send_input('n')

    # Close stdin to end process
    proc.stdin.close()

    # Read remaining output
    read_output()

    proc.wait()

if __name__ == "__main__":
    run_trading_bot_test()
