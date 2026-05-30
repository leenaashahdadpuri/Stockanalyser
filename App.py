import streamlit as st
import yfinance as yf
import pandas as pd
import requests  # <-- NEW: Needed to create a browser session

# Set up a wide layout for a clean dashboard view
st.set_page_config(layout="wide")
st.title("📊 Custom Wall Street Analyst Dashboard")
st.write("Type any US stock ticker below to pull real-time data, company info, and market consensus.")

# 1. TEXT INPUT FIELD
user_input = st.text_input("Enter Stock Ticker:", "NVDA")
selected_ticker = user_input.strip().upper()

# Run the data pipeline only if the text field isn't empty
if selected_ticker:
    
    # --- FIXED: Mimic a regular web browser to bypass rate-limits ---
    custom_session = requests.Session()
    custom_session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })
    
    # Attach the authenticated session directly into the Ticker object
    stock = yf.Ticker(selected_ticker, session=custom_session)
    
    # --- Data Fetching Block ---
    try:
        info = stock.info
        
        # Check if yfinance returned a valid profile
        if not info or "longName" not in info:
            st.error(f"Could not find any data for ticker '{selected_ticker}'. Please check the spelling and try again.")
            st.stop()
            
        company_name = info.get("longName", selected_ticker)
        summary = info.get("longBusinessSummary", "No description available.")
        current_rec = info.get("recommendationKey", "N/A").upper()
        target_price = info.get("targetMeanPrice", "N/A")
        current_price = info.get("currentPrice", "N/A")
    except Exception as e:
        st.error(f"Error retrieving data for '{selected_ticker}'. The ticker might be invalid, delisted, or Yahoo is rate-limiting the connection.")
        st.stop()

    # [The rest of your code remains exactly the same below this line]
