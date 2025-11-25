import pandas as pd
import yfinance as yf

df = pd.read_csv("sp_500_stocks.csv")

valid_tickers = []

for symbol in df["Ticker"]:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")

    if not hist.empty:  # means ticker works
        valid_tickers.append(symbol)

clean_df = df[df["Ticker"].isin(valid_tickers)]
clean_df.to_csv("sp_500_stocks_cleaned.csv", index=False)

print("Cleaning complete!")
print("Old tickers:", len(df))
print("Valid tickers:", len(clean_df))
print("New cleaned file saved as sp_500_stocks_cleaned.csv")
