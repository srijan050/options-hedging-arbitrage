import pandas as pd
from . import black_scholes as bs 
from . import config
import numpy as np

def calculate_theoretical_values(market_data, time_to_expiry):
    """
    Calculates Black-Scholes values and deltas for all options in the dataset.

    This function vectorizes the calculations for speed, applying the Black-Scholes
    formulas to entire columns at once instead of looping through each row.

    Args:
        market_data (pd.DataFrame): The preprocessed market data.
        time_to_expiry (pd.DataFrame): The time to expiry for each timestamp.

    Returns:
        pd.DataFrame: The input market_data DataFrame with new columns for
                      theoretical prices and deltas.
    """
    print("Calculating theoretical option values and deltas...")
    option_names = sorted(list(set([col[0] for col in market_data.columns if col[0] != 'Stock'])))
    
    market_data_calcs = market_data.copy()
    market_data_calcs['TTE'] = time_to_expiry['TimeToExpiry'].values

    for option in option_names:
        K = int(option[1:])
        S_ask, S_bid, T, r, sigma = (
            market_data_calcs[('Stock', 'AskPrice')], market_data_calcs[('Stock', 'BidPrice')],
            market_data_calcs['TTE'], config.RISK_FREE_RATE, config.VOLATILITY,
        )

        if 'C' in option:
            market_data_calcs[(option, 'Expected AskPrice')] = bs.call_value(S_ask, K, T, r, sigma)
            market_data_calcs[(option, 'Delta Short')] = -bs.call_delta(S_ask, K, T, r, sigma)
            market_data_calcs[(option, 'Expected BidPrice')] = bs.call_value(S_bid, K, T, r, sigma)
            market_data_calcs[(option, 'Delta Long')] = bs.call_delta(S_bid, K, T, r, sigma)
        elif 'P' in option:
            market_data_calcs[(option, 'Expected AskPrice')] = bs.put_value(S_bid, K, T, r, sigma)
            market_data_calcs[(option, 'Delta Short')] = -bs.put_delta(S_bid, K, T, r, sigma)
            market_data_calcs[(option, 'Expected BidPrice')] = bs.put_value(S_ask, K, T, r, sigma)
            market_data_calcs[(option, 'Delta Long')] = bs.put_delta(S_ask, K, T, r, sigma)

        market_data_calcs[(option, 'Expected AskPrice')] = round(market_data_calcs[(option, 'Expected AskPrice')], 2)
        market_data_calcs[(option, 'Expected BidPrice')] = round(market_data_calcs[(option, 'Expected BidPrice')], 2)

    market_data_calcs = market_data_calcs.drop(columns='TTE').sort_index(axis=1)
    print("Calculations complete.")
    return market_data_calcs

def run_trading_simulation(market_data_with_models):
    """
    Simulates the arbitrage strategy and delta hedging over the entire dataset.

    This function iterates through each time step, checks for arbitrage
    opportunities, simulates trades, and maintains a delta-neutral portfolio
    by adjusting the stock position.

    Args:
        market_data_with_models (pd.DataFrame): The market data enriched with
                                                Black-Scholes values and deltas.

    Returns:
        pd.DataFrame: A DataFrame containing the history of positions for all
                      instruments (options and the underlying stock).
    """
    print("Running trading simulation...")
    timestamp_index = market_data_with_models.index
    option_names = sorted(list(set([col[0] for col in market_data_with_models.columns if col[0] != 'Stock'])))

    log_data = {}
    for option in option_names:
        if 'C' in option:
            log_data[('Call Position', option)] = []
            log_data[('Call Delta', option)] = []
        if 'P' in option:
            log_data[('Put Position', option)] = []
            log_data[('Put Delta', option)] = []

    call_positions = {opt: 0.0 for opt in option_names if 'C' in opt}
    put_positions = {opt: 0.0 for opt in option_names if 'P' in opt}

    for _, row in market_data_with_models.iterrows():
        for option in option_names:
            trade_volume = 0
            model_ask, model_bid = row[(option, 'Expected AskPrice')], row[(option, 'Expected BidPrice')]
            market_ask, market_bid = row[(option, 'AskPrice')], row[(option, 'BidPrice')]
            
            if market_bid - model_ask >= config.ARBITRAGE_THRESHOLD:
                trade_volume = -row[(option, 'BidVolume')]
            elif model_bid - market_ask >= config.ARBITRAGE_THRESHOLD:
                trade_volume = row[(option, 'AskVolume')]
            
            if 'C' in option:
                call_positions[option] += trade_volume
                log_data[('Call Position', option)].append(call_positions[option])
                delta_val = row[(option, 'Delta Short')] if call_positions[option] < 0 else row[(option, 'Delta Long')]
                log_data[('Call Delta', option)].append(abs(call_positions[option]) * delta_val)
            elif 'P' in option:
                put_positions[option] += trade_volume
                log_data[('Put Position', option)].append(put_positions[option])
                delta_val = row[(option, 'Delta Short')] if put_positions[option] < 0 else row[(option, 'Delta Long')]
                log_data[('Put Delta', option)].append(abs(put_positions[option]) * delta_val)
    
    trades_df = pd.DataFrame(log_data, index=timestamp_index)
    trades_df = trades_df.reindex(sorted(trades_df.columns), axis=1)

    call_delta_cols = [col for col in trades_df.columns if col[0] == 'Call Delta']
    put_delta_cols = [col for col in trades_df.columns if col[0] == 'Put Delta']
    total_option_delta = trades_df[call_delta_cols].sum(axis=1) + trades_df[put_delta_cols].sum(axis=1)
    
    stock_position = -np.where(total_option_delta >= 0, np.floor(total_option_delta), np.ceil(total_option_delta))
    
    final_positions = pd.DataFrame(index=timestamp_index)
    for option in option_names:
        pos_key = ('Call Position', option) if 'C' in option else ('Put Position', option)
        final_positions[option] = trades_df[pos_key]
    final_positions['Stock'] = stock_position
    
    print("Simulation complete.")
    return final_positions.sort_index(axis=1)