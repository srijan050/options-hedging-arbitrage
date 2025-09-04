import pandas as pd

def load_and_preprocess_data(file_path):
    """
    Reads market data from a CSV and preprocesses it into a structured format.
    
    Args:
        file_path (str): The path to the CSV file.
        
    Returns:
        tuple: A tuple containing:
            - time_to_expiry (pd.DataFrame): DataFrame with time to expiry.
            - market_data (pd.DataFrame): Multi-index DataFrame with stock and options data.
    """
    print("Reading data from:", file_path)
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    
    # 1. Isolate the time to expiry data
    time_to_expiry = df.filter(like='TimeToExpiry')

    # 2. Isolate and structure the stock data
    stock_df = df.filter(like='-Stock')
    # We rename the columns to create a MultiIndex: Level 0 = 'Stock', Level 1 = 'BidPrice', etc.
    stock_df.columns = pd.MultiIndex.from_product([['Stock'], [col.split('-')[0] for col in stock_df.columns]])

    # 3. Isolate and structure the options data
    options_df = df.drop(columns=stock_df.columns.get_level_values(1) + '-Stock')
    options_df = options_df.drop(columns=['TimeToExpiry'])
    # We create a MultiIndex here too: Level 0 = 'C70', Level 1 = 'BidPrice', etc.
    options_df.columns = pd.MultiIndex.from_tuples(
        [(col.split('-')[1], col.split('-')[0]) for col in options_df.columns]
    )

    # 4. Combine them into a single, clean DataFrame
    market_data = pd.concat([stock_df, options_df], axis=1).sort_index(axis=1)

    print("Data loaded and preprocessed successfully.")
    return time_to_expiry, market_data