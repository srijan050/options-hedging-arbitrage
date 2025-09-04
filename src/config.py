# src/config.py

# --- File Paths ---
DATA_FILE = 'data/Options Arbitrage.csv'

# --- Model Parameters ---
# The annual risk-free interest rate. 
# We use 0.0 for simplicity, but in reality, this would be the yield on a government bond.
RISK_FREE_RATE = 0.0

# The assumed annual volatility of the underlying stock.
# This is the most critical parameter in option pricing.
VOLATILITY = 0.20  # This means we assume the stock's price has a 20% annualized standard deviation.

# --- Strategy Parameters ---
# The minimum price discrepancy needed to trigger a trade.
ARBITRAGE_THRESHOLD = 0.10