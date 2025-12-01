"""
Equal-Weight S&P 500 Index Fund (Pure Equal Weight Version)

This version:
- Reads CSV of S&P 500 tickers
- Fetches latest close prices with fallback
- Assigns TRUE equal-weight allocation:
      position_size = portfolio_value / total_stocks
      shares = floor(position_size / price)
- Saves final dataframe
"""

import math
import time
import numpy as np
import pandas as pd
import yfinance as yf


# ----------------------------------------------
# FIX TICKERS FOR YAHOO FINANCE
# ----------------------------------------------
def fix_ticker(symbol: str) -> str:
    if "." in symbol:
        return symbol.replace(".", "-")
    return symbol


# ----------------------------------------------
# BATCH PRICE DOWNLOAD (WITH FALLBACK)
# ----------------------------------------------
def _download_close_prices(tickers_list, period="1d"):
    if not tickers_list:
        return pd.DataFrame()

    try:
        data = yf.download(
            tickers_list,
            period=period,
            group_by='ticker',
            threads=True,
            progress=False
        )
    except:
        return pd.DataFrame()

    # Multi-Index case (most common)
    if isinstance(data, pd.DataFrame) and isinstance(data.columns, pd.MultiIndex):
        try:
            close_df = data.xs("Close", axis=1, level=1)
        except:
            close_df = pd.DataFrame()
        return close_df

    # Single-ticker case
    if isinstance(data, pd.DataFrame) and "Close" in data.columns:
        if len(tickers_list) == 1:
            return pd.DataFrame({tickers_list[0]: data["Close"]})

    return pd.DataFrame()


# ----------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------
def create_equal_weight_portfolio(portfolio_value: float,
                                  csv_path="sp_500_stocks_cleaned.csv",
                                  sleep_between=0.02):

    stocks = pd.read_csv(csv_path)

    tickers_raw = stocks["Ticker"].astype(str).to_list()
    tickers_list = [fix_ticker(t) for t in tickers_raw]

    # Fetch prices
    close_df = _download_close_prices(tickers_list)

    rows = []
    failed_symbols = []

    for ticker_symbol in tickers_list:
        price = np.nan

        # Try from batch
        if not close_df.empty and ticker_symbol in close_df.columns:
            try:
                price = float(close_df[ticker_symbol].dropna().iloc[-1])
            except:
                price = np.nan

        # Single ticker fallback
        if np.isnan(price):
            try:
                tmp = yf.Ticker(ticker_symbol).history(period="1d")
                if not tmp.empty:
                    price = float(tmp["Close"].iloc[-1])
            except:
                price = np.nan

        # Market Cap (optional)
        market_cap = "N/A"
        try:
            tkr = yf.Ticker(ticker_symbol)
            mc = None

            try:
                mc = tkr.fast_info.get("market_cap")
            except:
                mc = None

            if mc is None:
                info = {}
                try:
                    info = tkr.info
                except:
                    pass
                market_cap = info.get("marketCap", "N/A")
            else:
                market_cap = mc

        except:
            market_cap = "N/A"

        if np.isnan(price):
            failed_symbols.append(ticker_symbol)
        else:
            rows.append([ticker_symbol, price, market_cap, 0, 0.0])

        time.sleep(sleep_between)

    # Build dataframe
    cols = ["Ticker", "Stock Price", "Market Captilization",
            "Number Of Shares to Buy", "Amount Invested"]
    final_dataframe = pd.DataFrame(rows, columns=cols)

    if final_dataframe.empty:
        return final_dataframe, failed_symbols

    # ----------------------------------------------
    # PURE EQUAL-WEIGHT MATH (YOUR ORIGINAL LOGIC)
    # ----------------------------------------------
    n_stocks = len(final_dataframe.index)
    position_size = float(portfolio_value) / n_stocks

    for idx in final_dataframe.index:
        price = final_dataframe.at[idx, "Stock Price"]
        shares = math.floor(position_size / price)

        final_dataframe.at[idx, "Number Of Shares to Buy"] = shares
        final_dataframe.at[idx, "Amount Invested"] = round(shares * price, 2)

    return final_dataframe, failed_symbols


# ----------------------------------------------
# RUN FROM TERMINAL (OPTIONAL)
# ----------------------------------------------
if __name__ == "__main__":
    import sys

    pv = 100000
    if len(sys.argv) > 1:
        try:
            pv = float(sys.argv[1])
        except:
            pass

    df, failed = create_equal_weight_portfolio(pv)
    print("Total Stocks:", len(df))
    print("Failed:", len(failed))
    print(df.head(10))
