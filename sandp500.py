import numpy as np
import pandas as pd
import math
import yfinance as yf
import time

# -------------------------
# Helper Functions
# -------------------------

def fix_ticker(symbol):
    """Fix ticker symbols for Yahoo Finance format (e.g., BRK.B -> BRK-B)."""
    if "." in symbol:
        return symbol.replace(".", "-")
    return symbol

def fetch_stock_data(stocks_csv="sp_500_stocks_cleaned.csv", sleep_time=0.05):
    """
    Fetch prices and market capitalization for S&P 500 stocks.
    
    Returns:
        pd.DataFrame: DataFrame with columns ['Ticker', 'Stock Price', 'Market Captilization', 'Number Of Shares to Buy', 'Amount Invested']
    """
    # Read CSV
    stocks = pd.read_csv(stocks_csv)
    
    # Fix tickers for Yahoo Finance
    tickers_list = [fix_ticker(sym) for sym in stocks['Ticker']]
    
    # Batch download prices for speed
    data = yf.download(tickers_list, period="1d", group_by='ticker', threads=True, progress=False)
    
    final_df = []
    failed_symbols = []
    
    for ticker_symbol in tickers_list:
        try:
            # Fetch price
            if ticker_symbol in data:
                price = data[ticker_symbol]['Close'].iloc[-1]
            else:
                price = "N/A"
            
            # Fetch market cap
            ticker = yf.Ticker(ticker_symbol)
            market_cap = ticker.fast_info.get("market_cap")
            if market_cap is None:
                try:
                    info = ticker.info
                    market_cap = info.get("marketCap", "N/A")
                except:
                    market_cap = "N/A"
            
            if price == "N/A":
                failed_symbols.append(ticker_symbol)
            
            final_df.append([ticker_symbol, price, market_cap, 0, 0.0])
            
            # Small delay to avoid API rate limits
            time.sleep(sleep_time)
        
        except:
            final_df.append([ticker_symbol, "N/A", "N/A", 0, 0.0])
            failed_symbols.append(ticker_symbol)
    
    # Convert to DataFrame
    final_dataframe = pd.DataFrame(final_df, columns=['Ticker', 'Stock Price', 'Market Captilization', 'Number Of Shares to Buy', 'Amount Invested'])
    
    # Remove failed symbols
    final_dataframe = final_dataframe[final_dataframe['Stock Price'] != "N/A"].reset_index(drop=True)
    
    return final_dataframe

def allocate_portfolio(final_dataframe, portfolio_value=100000):
    """
    Calculate number of shares to buy and amount invested per stock for an equal-weight portfolio.
    
    Args:
        final_dataframe (pd.DataFrame): DataFrame from fetch_stock_data()
        portfolio_value (float): Total portfolio value
    
    Returns:
        pd.DataFrame: Updated DataFrame with allocation
    """
    position_size = portfolio_value / len(final_dataframe)
    
    for i in range(len(final_dataframe)):
        price = final_dataframe.loc[i, 'Stock Price']
        if price != "N/A":
            shares_to_buy = math.floor(position_size / price)
            final_dataframe.loc[i, 'Number Of Shares to Buy'] = shares_to_buy
            final_dataframe.loc[i, 'Amount Invested'] = round(shares_to_buy * price, 2)
    
    return final_dataframe

def save_portfolio(final_dataframe, filename="equal_weight_sp500.xlsx"):
    """
    Save portfolio DataFrame to Excel.
    """
    final_dataframe.to_excel(filename, index=False)
    print(f"✅ Portfolio saved to '{filename}'")

# -------------------------
# Example Usage
# -------------------------
if __name__ == "__main__":
    df = fetch_stock_data("sp_500_stocks_cleaned.csv")
    df = allocate_portfolio(df, portfolio_value=100000)
    save_portfolio(df)
    print(df.head(10))
