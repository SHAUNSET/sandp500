import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import math
import plotly.express as px

st.set_page_config(page_title="Equal-Weight S&P 500 Simulator", layout="wide")

st.title("📊 Equal-Weight S&P 500 Simulator")

# --- User Input ---
portfolio_input = st.number_input(
    "💵 Enter Your Portfolio Value ($):",
    min_value=1.0, value=100000.0, step=1000.0
)
portfolio_value = float(portfolio_input)

st.write("---")

# --- Load Tickers ---
stocks = pd.read_csv("sp_500_stocks_cleaned.csv")

def fix_ticker(symbol):
    return symbol.replace(".", "-") if "." in symbol else symbol

tickers_list = [fix_ticker(t) for t in stocks["Ticker"]]

# --- Fetch Latest Prices ---
with st.spinner("⏳ Fetching latest prices from Yahoo Finance..."):
    try:
        data = yf.download(
            tickers_list,
            period="1d",
            progress=False,
            threads=True
        )["Close"]
    except:
        st.error("⚠ Error fetching stock prices. Try again later.")
        st.stop()

# Build main DataFrame
final_dataframe = pd.DataFrame(columns=["Ticker", "Price", "Number Of Shares", "Amount Invested"])

for ticker in tickers_list:
    try:
        price = data[ticker].iloc[-1]
        final_dataframe.loc[len(final_dataframe)] = [ticker, price, 0, 0.0]
    except:
        pass

# Drop missing prices
final_dataframe.dropna(inplace=True)

# --- TRUE EQUAL WEIGHT MATH ---
position_size = portfolio_value / len(final_dataframe)

final_dataframe["Number Of Shares"] = final_dataframe["Price"].apply(
    lambda price: math.floor(position_size / price)
)

final_dataframe["Amount Invested"] = final_dataframe["Number Of Shares"] * final_dataframe["Price"]

# Summary stats
total_invested = final_dataframe["Amount Invested"].sum()
remaining_cash = portfolio_value - total_invested

st.success("🎉 Allocation Completed Successfully!")

# Sort for display
final_dataframe.sort_values(by="Amount Invested", ascending=False, inplace=True)

# --- Display Results ---
st.subheader("📈 Top 20 Stocks Allocation")
st.dataframe(final_dataframe.head(20), use_container_width=True)

st.write(f"### 💵 Total Invested: ${total_invested:,.2f}")
st.write(f"### 💰 Remaining Cash: ${remaining_cash:,.2f}")

st.write("---")

# --- Graphs Section ---
st.subheader("📊 Investment Distribution Charts")

col1, col2 = st.columns(2)

# PIE CHART
with col1:
    fig_pie = px.pie(
        final_dataframe.head(20),
        names="Ticker",
        values="Amount Invested",
        title="Top 20 Stocks — Allocation Pie Chart"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# BAR CHART
with col2:
    fig_bar = px.bar(
        final_dataframe.head(20),
        x="Ticker",
        y="Amount Invested",
        title="Top 20 Stocks — Amount Invested",
        text_auto='.2s'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Excel Download ---
excel_file = "equal_weight_sp500.xlsx"
final_dataframe.to_excel(excel_file, index=False)

st.download_button(
    "📥 Download Excel File",
    data=open(excel_file, "rb").read(),
    file_name=excel_file
)

st.write("---")
st.caption("Built by Shaunak 🚀 Equal-Weight S&P 500 Allocation Engine")
