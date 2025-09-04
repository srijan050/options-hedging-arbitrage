import pandas as pd
import numpy as np

def calculate_pnl(positions, market_data):
    print("Calculating PnL...")
    
    trades_diff = positions.diff().iloc[1:]
    market_data_for_pnl = market_data.iloc[1:]
    cashflow_df = pd.DataFrame(index=trades_diff.index)

    for instrument in positions.columns:
        instrument_trades = trades_diff[instrument]
        ask_prices = market_data_for_pnl[(instrument, 'AskPrice')]
        bid_prices = market_data_for_pnl[(instrument, 'BidPrice')]
        cashflow_df[instrument] = np.where(instrument_trades >= 0, -instrument_trades * ask_prices, -instrument_trades * bid_prices)
    total_cashflow = cashflow_df.sum().sum()

    final_positions = positions.iloc[-1]
    last_market_prices = market_data.iloc[-1]
    valuation = sum(
        pos * last_market_prices[(inst, 'BidPrice' if pos > 0 else 'AskPrice')]
        for inst, pos in final_positions.items() if pos != 0
    )

    print("PnL calculation complete.")
    return {
        'total_cashflow': total_cashflow,
        'final_valuation': valuation,
        'total_pnl': total_cashflow + valuation
    }