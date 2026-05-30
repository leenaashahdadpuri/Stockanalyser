import streamlit as st
import requests
import pandas as pd
import datetime

# Set up a wide layout for a clean dashboard view
st.set_page_config(layout="wide")
st.title("📊 Open Financial Analytics & Growth Dashboard")
st.write("Powered by Finnhub API (Unrestricted Free Tier Configuration)")

# Setup Input Fields for Ticker and API Token
col_input1, col_input2 = st.columns([1, 2])
with col_input1:
    user_input = st.text_input("Enter Stock Ticker:", "NVDA")
    selected_ticker = user_input.strip().upper()
with col_input2:
    api_token = st.text_input("Enter Finnhub API Token/Key:", type="password")

# Memory Cache to preserve request limits and optimize page reloads
@st.cache_data(ttl=300, show_spinner="Gathering asset sheets from data network...")
def fetch_finnhub_data(ticker, token):
    # Core Endpoint 1: Active profile metrics (industry, capitalizations, shares out)
    profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={token}"
    # Core Endpoint 2: Real-time market valuation rates
    quote_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={token}"
    
    # Core Endpoint 3: Continuous historical pricing bars
    end_date = int(datetime.datetime.now().timestamp())
    start_date = end_date - (5 * 365 * 24 * 60 * 60) # Fetch up to trailing 5 years
    history_url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={start_date}&to={end_date}&token={token}"
    
    try:
        p_res = requests.get(profile_url).json()
        q_res = requests.get(quote_url).json()
        h_res = requests.get(history_url).json()
        return p_res, q_res, h_res
    except Exception as e:
        return None, None, None

# Launch data engine only when user fills both boxes
if selected_ticker and api_token:
    profile_res, quote_res, history_res = fetch_finnhub_data(selected_ticker, api_token)
    
    # Validate token authentication responses
    if not profile_res or "name" not in profile_res:
        st.error(f"⚠️ Could not pull profiles for '{selected_ticker}'.")
        st.info("💡 **Resolution Checklist:**\n"
                "1. Confirm your Finnhub token was copied completely without trailing spaces.\n"
                "2. Try a universally supported core asset ticker like **NVDA**, **AAPL**, or **TSLA**.")
        st.stop()
        
    # Content Variable Extractions
    company_name = profile_res.get("name", selected_ticker)
    industry = profile_res.get("finnhubIndustry", "N/A")
    mkt_cap = profile_res.get("marketCapitalization", 0.0)
    shares_outstanding = profile_res.get("shareOutstanding", 0.0)
    
    current_price = quote_res.get("c", 0.0) # 'c' represents Closing Current Rate
    previous_close = quote_res.get("pc", 0.0)
    price_change = current_price - previous_close
    
    # Display Layout Headers
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"{company_name} ({selected_ticker})")
        st.subheader("🏢 Corporate Profile Metadata")
        st.write(f"**Primary Industry Classification:** {industry}")
        st.write(f"**Total Capital Shares Outstanding:** {shares_outstanding:,.2f} million shares")
    with col2:
        st.subheader("📈 Core Pricing Information")
        st.metric(label="Current Share Price", value=f"${current_price:,.2f}", delta=f"{price_change:+.2f}")
        st.metric(label="Market Capitalization Value", value=f"${mkt_cap:,.2f}M")
            
    st.markdown("---")
    
    # --- Timeline Performance Charts ---
    st.subheader("📈 Historical Growth Performance Tracking")
    
    # Check if Finnhub returned valid historical candle lists ('s' state must be 'ok')
    if history_res and history_res.get("s") == "ok":
        # Extract closing arrays ('c') and timestamp vectors ('t')
        close_prices = history_res.get("c", [])
        timestamps = history_res.get("t", [])
        
        # Build pandas mapping frame
        price_df = pd.DataFrame({"Close Price": close_prices})
        price_df.index = pd.to_datetime(timestamps, unit='s')
        price_df = price_df.sort_index(ascending=True)
        
        tab1, tab2, tab3 = st.tabs(["1 Week Growth", "1 Month Growth", "Maximum Growth History"])
        
        with tab1:
            week_df = price_df.tail(7)
            if not week_df.empty:
                first_val = week_df["Close Price"].iloc[0]
                last_val = week_df["Close Price"].iloc[-1]
                w_growth = ((last_val - first_val) / first_val) * 100
                st.metric("1-Week Performance Trend", f"{w_growth:+.2f}%")
                st.line_chart(week_df["Close Price"])
                
        with tab2:
            month_df = price_df.tail(30)
            if not month_df.empty:
                m_first_val = month_df["Close Price"].iloc[0]
                m_last_val = month_df["Close Price"].iloc[-1]
                m_growth = ((m_last_val - m_first_val) / m_first_val) * 100
                st.metric("1-Month Performance Trend", f"{m_growth:+.2f}%")
                st.line_chart(month_df["Close Price"])
                
        with tab3:
            if not price_df.empty:
                max_first_val = price_df["Close Price"].iloc[0]
                max_last_val = price_df["Close Price"].iloc[-1]
                max_growth = ((max_last_val - max_first_val) / max_first_val) * 100
                st.metric("All-Time Historical Performance Trend", f"{max_growth:+.2f}%")
                st.line_chart(price_df["Close Price"])
    else:
        st.info("Historical line tracking metrics are preparing datasets or waiting on server propagation.")

    st.markdown("---")
    
    # --- Major Stakeholder & Corporate Ownership Breakdown ---
    st.subheader("🐋 Major Stakeholder & Corporate Ownership Breakdown")
    
    ipo_date = profile_res.get("ipo", "N/A")
    country = profile_res.get("country", "N/A")
    currency = profile_res.get("currency", "N/A")
    exchange = profile_res.get("exchange", "N/A")
    
    ownership_data = {
        "Initial Public Offering (IPO Date)": [ipo_date],
        "Primary Listed Exchange Location": [exchange],
        "Reporting Base Country Code": [country],
        "Standard Asset Trade Currency": [currency]
    }
    
    ownership_df = pd.DataFrame(ownership_data)
    st.dataframe(ownership_df, use_container_width=True, hide_index=True)
    
elif not api_token:
    st.info("🔑 Please enter your Finnhub API Token above to boot your live tracking analytics framework.")
