# app.py
import streamlit as st
import pandas as pd
from finalsandp import create_equal_weight_portfolio

st.title("📊 Equal-Weight S&P 500 Portfolio Builder")
st.write("Enter the total value of your portfolio to calculate an equal-weight S&P 500 allocation.")

# User input for portfolio value
portfolio_value = st.number_input(
    "Enter your portfolio value ($):", 
    min_value=1000, max_value=10000000, value=100000, step=1000
)

# Button to calculate
if st.button("Build Portfolio"):
    with st.spinner("Fetching stock data... this may take a few seconds"):
        df = create_equal_weight_portfolio(portfolio_value)

    if df.empty:
        st.error("❌ No valid stock data fetched. Check your CSV or internet connection.")
    else:
        st.success("✅ Portfolio calculated successfully!")
        st.dataframe(df.head(20))  # show first 20 rows
        # Optionally save
        df.to_excel("equal_weight_sp500.xlsx", index=False)
        st.write("💾 Portfolio saved to 'equal_weight_sp500.xlsx'")
