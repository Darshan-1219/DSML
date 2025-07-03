import streamlit as st
import pandas as pd
import yfinance as yf
import stock_api as stock_api

st.title("Stock Analysis")

st.sidebar.header("User Input")

def get_user_input():
    stock_symbol = st.sidebar.text_input("Stock Symbol", "^NSEI", help="Enter the stock symbol (e.g., ^NSEI for Nifty 50)")
    start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2025-06-27"))
    end_date = st.sidebar.date_input("End Date", pd.to_datetime(pd.Timestamp.today()))
    return stock_symbol, start_date, end_date

stock_symbol, start_date, end_date = get_user_input()

# ...existing code...

data = yf.download(stock_symbol, start=start_date, end=end_date)

if data.empty:
    st.error("No data found. Please check the stock symbol and date range.")
else:
    st.subheader("Raw Data")
    st.write(data)
    st.subheader("Data Statistics")
    st.write(data.describe())

# ...existing code...

import requests

# ...existing code...

# st.subheader("Options Data")
# try:
#     response = requests.get("http://localhost:5000/api/option_chain")
#     if response.status_code == 200:
#         options_data = response.json()
#         st.write(options_data)
#     else:
#         st.error(f"No options data found. Status code: {response.status_code}")
# except Exception as e:
#     st.error(f"Error fetching options data: {e}")


st.subheader("Options Data")
try:
   
    params = {"symbol": stock_symbol}
    if params["symbol"].startswith('^NSEI'):
        params["symbol"] = 'NIFTY'
    elif params["symbol"].startswith('^BSESN'):
        params["symbol"] = 'SENSEX'
    response = requests.get("http://localhost:5000/api/option_chain", params=params)
    if response.status_code == 200:
        options_data = response.json()
        # Adjust the key below to match the structure of your JSON
        if "records" in options_data and "data" in options_data["records"]:
            df = pd.DataFrame(options_data["records"]["data"])
            st.dataframe(df)
        else:
            st.write(options_data)  # fallback if structure is different
    else:
        st.error(f"No options data found. Status code: {response.status_code}")
except Exception as e:
    st.error(f"Error fetching options data: {e}")