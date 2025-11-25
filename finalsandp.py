# finalsandp.py
import pandas as pd
import yfinance as yf
import math
import time

def fix_ticker(symbol):
    """Fix Yahoo Finance tickers (e.g., BRK.B -> BRK-B)"""
    return symbol.replace(".", "-") if "." in symbol else symbol

def create_equal_weight_portfolio(portfolio_value, csv_path="sp_500_stocks_cleaned.csv"):
    """
    Fetch S&P 500 stock data and compute an equal-weight portfolio.

    Args:
        portfolio_value (float): Total portfolio value in dollars
        csv_path (str): Path to CSV of tickers

    Returns:
        pd.DataFrame: Portfolio with ticker, price, market cap, shares to buy, amount invested
    """
    # Load tickers
    stocks = pd.read_csv(csv_path)

    my_columns = ['Ticker', 'Stock Price', 'Market Captilization', 'Number Of Shares to Buy', 'Amount Invested']
    final_dataframe = pd.DataFrame(columns=my_columns)

    tickers_list = [fix_ticker(sym) for sym in stocks['Ticker']]
    
    # Batch download prices
    try:
        data = yf.download(tickers_list, period="1d", group_by='ticker', threads=True, progress=False)
    except Exception as e:
        print("❌ Error fetching data:", e)
        return pd.DataFrame()  # empty DF
    
    final_df = []
    for ticker_symbol in tickers_list:
        try:
            # Price
            if ticker_symbol in data:
                price = data[ticker_symbol]['Close'].iloc[-1]
            else:
                price = "N/A"

            # Market cap
            ticker = yf.Ticker(ticker_symbol)
            market_cap = ticker.fast_info.get("market_cap")
            if market_cap is None:
                try:
                    info = ticker.info
                    market_cap = info.get("marketCap", "N/A")
                except:
                    market_cap = "N/A"

            final_df.append([ticker_symbol, price, market_cap, 0, 0.0])
            time.sleep(0.05)  # rate limit

        except:
            final_df.append([ticker_symbol, "N/A", "N/A", 0, 0.0])

    final_dataframe = pd.DataFrame(final_df, columns=my_columns)

    # Remove failed symbols
    final_dataframe = final_dataframe[final_dataframe['Stock Price'] != "N/A"].reset_index(drop=True)

    if final_dataframe.empty:
        print("❌ No valid stock data fetched. Check CSV or internet connection.")
        return pd.DataFrame()  # empty DF

    # Portfolio allocation
    position_size = portfolio_value / len(final_dataframe)
    for i in range(len(final_dataframe)):
        price = final_dataframe.loc[i, 'Stock Price']
        shares_to_buy = math.floor(position_size / price)
        final_dataframe.loc[i, 'Number Of Shares to Buy'] = shares_to_buy
        final_dataframe.loc[i, 'Amount Invested'] = round(shares_to_buy * price, 2)

    return final_dataframe
