from . import config
from . import data_loader
from . import strategy
from . import performance

def run_backtest():
    """
    Main function to run the entire arbitrage backtest from start to finish.
    """
    print("--- Starting Options Arbitrage Backtest ---")
    
    time_to_expiry, market_data = data_loader.load_and_preprocess_data(config.DATA_FILE)
    
    market_data_with_models = strategy.calculate_theoretical_values(
        market_data, time_to_expiry
    )
    
    positions = strategy.run_trading_simulation(market_data_with_models)
    
    pnl_results = performance.calculate_pnl(positions, market_data)

    print("\n--- Backtest Results ---")
    print(f"Total Realized Cashflow: €{pnl_results['total_cashflow']:.2f}")
    print(f"Final Portfolio Valuation (Unrealized PnL): €{pnl_results['final_valuation']:.2f}")
    print(f"Total Strategy PnL: €{pnl_results['total_pnl']:.2f}")
    print("------------------------")

if __name__ == '__main__':
    run_backtest()