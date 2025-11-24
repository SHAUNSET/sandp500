'''
Equal-Weight S&P 500 Index Fund

Introduction & Library Imports
The S&P 500 is the world's most popular stock market index. The largest fund that is benchmarked to this index is the SPDR® S&P 500® ETF Trust. It has more than US$250 billion of assets under management.

The goal of this section of the course is to create a Python script that will accept the value of your portfolio and tell you how many shares of each S&P 500 constituent you should purchase to get an equal-weight version of the index fund.

Library Imports
The first thing we need to do is import the open-source software libraries that we'll be using in this tutorial.
'''
import numpy as np
import pandas as pd 
import requests 
import math
import yfinance as yf
import time


'''
Importing Our List of Stocks
The next thing we need to do is import the constituents of the S&P 500.

These constituents change over time, so in an ideal world you would connect directly to the index provider (Standard & Poor's) and pull their real-time constituents on a regular basis.

Paying for access to the index provider's API is outside of the scope .
'''

stocks = pd.read_csv("sp_500_stocks.csv")
print(stocks.head())


'''
Making Our First API Call
Now it's time to structure our API calls to AlphaVantage.

We need the following information from the API:

Market capitalization for each stock
Price of each stock
'''

symbol = 'AAPL'
ticker = yf.Ticker(symbol)
price = ticker.history(period="1d")['Close'].iloc[-1]

# --- FIXED & RELIABLE MARKET CAP LOGIC ---
market_cap = ticker.fast_info.get("market_cap")
if market_cap is None:
    try:
        market_cap = ticker.info.get("marketCap", "N/A")
    except:
        market_cap = "N/A"

print("Market Cap:", market_cap)
print("Price:", price)


'''
Adding Our Stocks Data to a Pandas DataFrame
The next thing we need to do is add our stock's price and market capitalization to a pandas DataFrame. 
Think of a DataFrame like the Python version of a spreadsheet. It stores tabular data.
'''

my_columns = ['Ticker' , 'Stock Price' , 'Market Captilization' , 'Number of shares to buy']
final_dataframe = pd.DataFrame(columns = my_columns)

def fix_ticker(symbol):
    if "." in symbol:
        return symbol.replace(".", "-")
    return symbol

for symbol in stocks['Ticker']:

    yf_symbol = fix_ticker(symbol)

    # --- NEW: small delay to protect from rate limits ---
    time.sleep(0.10)

    try:
        ticker = yf.Ticker(yf_symbol)

        hist = ticker.history(period="1d", timeout=5)
        if hist.empty:
            price = "N/A"
        else:
            price = hist['Close'].iloc[-1]

        # --- FIXED & RELIABLE MARKET CAP LOGIC ---
        market_cap = ticker.fast_info.get("market_cap")
        if market_cap is None:
            try:
                info = ticker.info
                market_cap = info.get("marketCap", "N/A")
            except:
                market_cap = "N/A"

    except Exception:
        price = "N/A"
        market_cap = "N/A"

    final_dataframe = pd.concat(
        [final_dataframe, pd.DataFrame([[symbol, price, market_cap, 'N/A']], columns=my_columns)],
        ignore_index=True
    )


portfolio_size = input("Enter Value of Portfolio : ")

try:
    val = float(portfolio_size)
except ValueError:
    print("That's not a number! \n Try again:")
    portfolio_size = input("Enter the value of your portfolio:")


position_size = float(portfolio_size) / len(final_dataframe.index)

for i in range(0, len(final_dataframe['Ticker'])-1):
    if final_dataframe['Stock Price'][i] != "N/A":
        final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(
            position_size / final_dataframe['Stock Price'][i]
        )
    else:
        final_dataframe.loc[i, 'Number Of Shares to Buy'] = "N/A"

final_dataframe
