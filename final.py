import numpy as np
import pandas as pd
import math
import yfinance as yf
import time
import streamlit as st
import plotly.express as px

# --- Streamlit UI ---
st.set_page_config(page_title="Equal-Weight S&P 500 Simulator", layout="wide")
st.title("📈 Equal-Weight S&P 500 Index Fund Simulator")

# Sidebar for portfolio input
st.sidebar.header("Portfolio Settings")
portfolio_input = st.sidebar.number_input("Enter Your Portfolio Value ($)", min_value=1000, value=100000, step=1000)

# --- Load S&P 500 tickers ---
stocks = pd.read_csv("sp_500_stocks_cleaned.csv")

# Fix tickers for Yahoo Finance
def fix_ticker(symbol):
    return symbol.replace(".", "-") if "." in symbol else symbol

tickers_list = [fix_ticker(t) for t in stocks['Ticker']]

# Download price data
st.info("Fetching latest stock prices...")
data = yf.download(tickers_list, period="1d", group_by='ticker', threads=True, progress=False)

# Build DataFrame
final_df = []
failed_symbols = []

with st.spinner("Processing stocks..."):
    for ticker_symbol in tickers_list:
        try:
            price = data[ticker_symbol]['Close'].iloc[-1] if ticker_symbol in data else np.nan
            ticker = yf.Ticker(ticker_symbol)
            market_cap = ticker.fast_info.get("market_cap") or ticker.info.get("marketCap", np.nan)

            if np.isnan(price):
                failed_symbols.append(ticker_symbol)
                continue

            final_df.append([ticker_symbol, price, market_cap, 0, 0.0])
            time.sleep(0.02)  # slight delay for API
        except:
            failed_symbols.append(ticker_symbol)

final_dataframe = pd.DataFrame(final_df, columns=['Ticker', 'Stock Price', 'Market Cap', 'Number Of Shares to Buy', 'Amount Invested'])

# --- True Equal-Weight Allocation ---
remaining_cash = portfolio_input
final_dataframe['Number Of Shares to Buy'] = 0
final_dataframe['Amount Invested'] = 0.0

while True:
    affordable_stocks = final_dataframe[final_dataframe['Stock Price'] <= remaining_cash]
    if affordable_stocks.empty:
        break

    equal_alloc = remaining_cash / len(affordable_stocks)
    for i, row in affordable_stocks.iterrows():
        price = row['Stock Price']
        shares = math.floor(equal_alloc / price)
        if shares > 0:
            final_dataframe.at[i, 'Number Of Shares to Buy'] += shares
            invested = shares * price
            final_dataframe.at[i, 'Amount Invested'] += invested
            remaining_cash -= invested

    if all(math.floor(equal_alloc / row['Stock Price']) == 0 for i, row in affordable_stocks.iterrows()):
        break

# --- Display Results ---
st.success("✅ Portfolio allocation complete!")
st.write(f"💰 Remaining Cash: ${remaining_cash:.2f}")
st.write(f"❌ Failed tickers (prices unavailable): {failed_symbols}")

st.subheader("Top 15 Stock Allocations")
st.dataframe(final_dataframe.sort_values("Amount Invested", ascending=False).head(15))

# --- Plot Investment Allocation ---
fig = px.bar(final_dataframe.sort_values("Amount Invested", ascending=False).head(20),
             x='Ticker', y='Amount Invested', text='Number Of Shares to Buy',
             title="Top 20 Stocks Investment Allocation")
fig.update_traces(texttemplate='%{text} shares', textposition='outside')
fig.update_layout(yaxis_title="Amount Invested ($)")
st.plotly_chart(fig, use_container_width=True)

# --- Save to Excel ---
final_dataframe.to_excel("equal_weight_sp500.xlsx", index=False)
st.info("Portfolio saved to 'equal_weight_sp500.xlsx'")
