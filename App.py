import streamlit as st
import requests
import pandas as pd

# Set up a wide layout for a clean dashboard view
st.set_page_config(layout="wide")
st.title("📊 Enterprise Analytics & Growth Dashboard")
st.write("Powered by FMP API (Up to 250 free daily queries to prevent rate limits)")

# Setup Input Fields for Ticker and API Key
col_input1, col_input2 = st.columns([1, 2])
with col_input1:
    user_input = st.text_input("Enter Stock Ticker:", "NVDA")
    selected_ticker = user_input.strip().upper()
with col_input2:
    api_key = st.text_input("Enter FinancialModelingPrep (FMP) API Key:", type="password")

# Cached Data Function to save your API keys and calls in local browser memory
@st.cache_data(ttl=1800, show_spinner="Loading global financial metrics...")
def fetch_fmp_data(ticker, key):
    # Endpoint 1: Profile contains descriptions, price, margins, and institutional stakes
    profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={key}"
    # Endpoint 2: Core historical daily pricing back to inception
    history_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={key}"
    
    try:
        p_res = requests.get(profile_url).json()
        h_res = requests.get(history_url).json()
        return p_res, h_res
    except Exception as e:
        return None, None

# Run data engine only if input variables exist
if selected_ticker and api_key:
    profile_data, history_data = fetch_fmp_data(selected_ticker, api_key)
    
    # 🛠️ BULLETPROOF GUARDRAIL: Pre-initialize an empty fallback dictionary
    profile = {}
    
    # Safely extract the profile dictionary ONLY if it is a list with elements inside
    if isinstance(profile_data, list) and len(profile_data) > 0:
        profile = profile_data[0]
    else:
        st.error(f"⚠️ Could not pull records for '{selected_ticker}'.")
        st.info("💡 **Why this happens:** \n"
                "1. Your FMP API key might be mistyped, inactive, or expired.\n"
                "2. The ticker requested might require a paid FMP tier. Try testing common default tickers like **NVDA**, **AAPL**, or **TSLA** to verify if your key is working.")
        st.stop() # Stops execution right here to prevent downstream crashes!
        
    # Double-check the historical chart data structure exists as well
    if not history_data or "historical" not in history_data:
        st.error("⚠️ Historical price series returned blank. This ticker might be restricted on the free plan.")
        st.stop()

    # Safe extraction using .get defaults
    company_name = profile.get("companyName", selected_ticker)
    summary = profile.get("description", "No description available.")
    current_price = profile.get("price", 0.0)
    target_price = profile.get("priceTarget", "N/A")
    
    # Display Core Profile Data Layout
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"{company_name} ({selected_ticker})")
        st.subheader("🏢 Company Summary")
        st.write(summary)
    with col2:
        st.subheader("📈 Core Pricing Information")
        st.metric(label="Current Rate / Share Price", value=f"${current_price:,.2f}")
        if target_price != "N
