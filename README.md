# Market-Neutral Options Arbitrage & Hedging

This project presents a Python-based backtesting framework designed to simulate a market-neutral options arbitrage strategy. The core of the strategy is to identify and capitalize on temporary mispricings between the market value of options and their theoretical “fair value,” as determined by the Black–Scholes model.

The system is engineered to be **market-neutral** by employing a continuous **delta-hedging** strategy, thereby isolating profit generation to the arbitrage edge itself rather than directional bets on the underlying stock.

---

### The Strategy: Core Concepts

The strategy operates on a few fundamental principles of quantitative finance.

#### 1. The Arbitrage Opportunity: Market vs. Model
The central idea is that an option’s price in the market can temporarily deviate from its theoretical fair value. Our model acts as a compass, telling us what the price *should* be.

- **Overpriced Option:** If the market’s *Bid Price* (what someone will pay us) is higher than our model’s *Ask Price* (what we think is a fair selling price), we have an opportunity to **sell (short)** the option.
- **Underpriced Option:** If the market’s *Ask Price* (what we have to pay) is lower than our model’s *Bid Price* (what we think is a fair buying price), we have an opportunity to **buy (long)** the option.

#### 2. The Valuation Model: Black–Scholes
To determine the theoretical “fair value,” we use the Black–Scholes model. This formula takes several key inputs to calculate an option’s price:

- \(S\): The current price of the underlying stock  
- \(K\): The option’s strike price  
- \(T\): The time remaining until the option expires (in years)  
- \(r\): The risk-free interest rate  
- \($\sigma\$): The annualized volatility of the stock (most critical input)

#### 3. The Risk Management: Delta Hedging
Trading an option exposes us to the risk of the stock price moving. To remain market-neutral, we hedge this risk using the option’s **Delta (\$\Delta\$)**.

- **What is Delta?** Delta measures the sensitivity of an option’s price to a €1 change in the stock’s price. For example, a call option with a delta of `+0.60` will increase in value by approximately €0.60 if the stock price rises by €1.  
- **Achieving Neutrality:** If our portfolio of options has a total delta of **+42.7**, it behaves like being long 42.7 shares of the stock. To neutralize this directional risk, we take the opposite position: we **sell (short) 43 shares** of the stock. Our portfolio’s net delta becomes ~0. This process is repeated at each timestamp to maintain neutrality.

---

### Mathematical Foundation

The backtester uses the following standard formulas.

**Black–Scholes (European options):**

$$
d_1 = \frac{\ln(S/K) + \left(r + \tfrac{1}{2}\sigma^2\right)T}{\sigma\sqrt{T}}
$$

$$
d_2 = d_1 - \sigma\sqrt{T}
$$

Call value:

$$
C(S,t) = S\,N(d_1) - K\,e^{-rT}\,N(d_2)
$$

Put value:

$$
P(S,t) = K\,e^{-rT}\,N(-d_2) - S\,N(-d_1)
$$

Here N($\cdot$) is the CDF of the standard normal distribution.

**Delta \($\Delta$\):**

$$
\Delta_{\text{call}} = N(d_1), \qquad
\Delta_{\text{put}}  = N(d_1) - 1
$$

---

### Project Structure

The project is organized into a modular `src` package for clarity and maintainability.

```

options\_arbitrage\_project/
├── data/
│   └── Options Arbitrage.csv
├── src/
│   ├── config.py          # Stores model and strategy parameters
│   ├── data_loader.py     # Reading and preprocessing of market data
│   ├── black_scholes.py   # Core mathematical formulas
│   ├── strategy.py        # Valuation, trade logic, and hedging
│   ├── performance.py     # Final Profit and Loss calculations
│   └── main.py            # Entry point to run the backtest
├── README.md
└── requirements.txt

```

---

### Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/srijan050/options-hedging-arbitrage
   cd options-hedging-arbitrage
   ```

2. **Create and Activate a Virtual Environment** (recommended)

   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   If you already have a `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

   Main dependencies: `pandas`, `numpy`, `scipy`.

---

### How to Run

From the repository root:

```bash
python -m src.main
```

*(The `-m` flag ensures relative imports inside `src` work properly.)*

---

### Results & Analysis

Sample results from the provided dataset:

```
--- Backtest Results ---
Total Realized Cashflow: €68985.54
Final Portfolio Valuation (Unrealized PnL): €-68802.71
Total Strategy PnL: €182.83
------------------------
```

**Interpretation**

The final PnL of **+€182.83** indicates marginal profitability. This is realistic and highlights real-world arbitrage constraints:

* **Transaction Costs:** Profits reflect small edges after crossing bid–ask spreads.
* **Hedging Friction:** Whole-share hedging leaves residual delta exposure.
* **Model Risk:** Results depend on the fixed volatility assumption (e.g., 20%). Different $\sigma$ values will change outcomes.

---

### Future Improvements

1. **Parameter Optimization:** Sweep `ARBITRAGE_THRESHOLD` and volatility to tune performance.
2. **Implied Volatility:** Use market-implied volatilities instead of a fixed $\sigma$.
3. **Cost Modeling:** Incorporate commissions and slippage.
4. **Portfolio Metrics:** Add Sharpe Ratio, Max Drawdown, Calmar Ratio, etc.

---
