import streamlit as st
import requests
import pandas as pd

# Set up a wide layout for a clean dashboard view
st.set_page_config(layout="wide")
st.title("📊 Enterprise Analytics & Growth Dashboard")
st.write("Powered by FMP API (Updated for 2026 API Endpoint Routing)")

# Setup Input Fields for Ticker and API Key
col_input1, col_input2 = st.columns([1, 2])
with col_input1:
    user_input = st.text_input("Enter Stock Ticker:", "NVDA")
    selected_ticker = user_input.strip().upper()
with col_input2:
    api_key = st.text_input("Enter FinancialModelingPrep (FMP) API Key:", type="password")

# Cached Data Function to save your API keys and calls in local browser memory
@st.cache_data(ttl=600, show_spinner="Loading global financial metrics...")
def fetch_fmp_data(ticker, key):
    # FIXED: Migrated from legacy endpoints to the new supported API v3 pathways
    profile_url = f"https://financialmodelingprep.com/api/v3/profile-metadata/{ticker}?apikey={key}"
    history_url = f"https://financialmodelingprep.com/api/v3/historical-chart/1day/{ticker}?apikey={key}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        p_res = requests.get(profile_url, headers=headers).json()
        h_res = requests.get(history_url, headers=headers).json()
        return p_res, h_res
    except Exception as e:
        return None, None

# Run data engine only if input variables exist
if selected_ticker and api_key:
    profile_data, history_data = fetch_fmp_data(selected_ticker, api_key)
    
    # Check if FMP explicitly returned a system error or invalid key warning
    if isinstance(profile_data, dict) and "Error Message" in profile_data:
        st.error(f"❌ API Error: {profile_data.get('Error Message')}")
        st.stop()
        
    profile = {}
    
    # Safely extract the profile dictionary ONLY if it is a list with elements inside
    if isinstance(profile_data, list) and len(profile_data) > 0:
        profile = profile_data[0]
    else:
        st.error(f"⚠️ Could not pull profile records for '{selected_ticker}'.")
        with st.expander("🔍 Click to view raw server response debug info"):
            st.write("Profile Response:", profile_data)
            st.write("History Response:", history_data)
        st.stop() 
        
    # Extract structural items cleanly using safe defaults
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
        st.metric(label="Current Rate / Share Price", value=f"${current_price:,.2f}" if current_price else "N/A")
        if target_price != "N/A" and target_price is not None:
            st.metric(label="Wall Street Target Mean", value=f"${float(target_price):,.2f}")
        else:
            st.metric(label="Wall Street Target Mean", value="N/A")
            
    st.markdown("---")
    
    # --- Timeline Performance Charts ---
    st.subheader("📈 Historical Growth Performance Tracking")
    
    # Check for new historical chart response format
    if isinstance(history_data, list) and len(history_data) > 0:
        # Turn historical array into a mapped pandas dataframe
        price_df = pd.DataFrame(history_data)
        price_df["date"] = pd.to_datetime(price_df["date"])
        price_df = price_df.set_index("date")
        
        # Fallback names in case FMP changes column headers from 'close' to 'price'
        close_col = "close" if "close" in price_df.columns else "price"
        price_df = price_df.rename(columns={close_col: "Close Price"})
        price_df = price_df.sort_index(ascending=True) # Sort chronological
        
        tab1, tab2, tab3 = st.tabs(["1 Week Growth", "1 Month Growth", "Maximum Growth History"])
        
        with tab1:
            week_df = price_df.tail(7)
            if not week_df.empty and "Close Price" in week_df.columns:
                first_val = week_df["Close Price"].iloc[0]
                last_val = week_df["Close Price"].iloc[-1]
                w_growth = ((last_val - first_val) / first_val) * 100
                st.metric("1-Week Performance Trend", f"{w_growth:+.2f}%")
                st.line_chart(week_df["Close Price"])
                
        with tab2:
            month_df = price_df.tail(30)
            if not month_df.empty and "Close Price" in month_df.columns:
                m_first_val = month_df["Close Price"].iloc[0]
                m_last_val = month_df["Close Price"].iloc[-1]
                m_growth = ((m_last_val - m_first_val) / m_first_val) * 100
                st.metric("1-Month Performance Trend", f"{m_growth:+.2f}%")
                st.line_chart(month_df["Close Price"])
                
        with tab3:
            if not price_df.empty and "Close Price" in price_df.columns:
                max_first_val = price_df["Close Price"].iloc[0]
                max_last_val = price_df["Close Price"].iloc[-1]
                max_growth = ((max_last_val - max_first_val) / max_first_val) * 100
                st.metric("All-Time Historical Performance Trend", f"{max_growth:+.2f}%")
                st.line_chart(price_df["Close Price"])
    else:
        st.info("Historical data timeline chart formatting limits reached on free key tier.")

    st.markdown("---")
    
    # --- Fundamental & Sector Metadata Metrics ---
    st.subheader("🐋 Major Stakeholder & Corporate Ownership Breakdown")
    
    mkt_cap = profile.get("mcap", "N/A")
    beta = profile.get("beta", "N/A")
    industry = profile.get("industry", "N/A")
    sector = profile.get("sector", "N/A")
    
    ownership_data = {
        "Market Capitalization": [f"${mkt_cap:,}" if isinstance(mkt_cap, (int, float)) else "N/A"],
        "Beta Volatility (Vs S&P 500)": [beta],
        "Primary Core Industry Segment": [industry],
        "Macro Sector Group": [sector]
    }
    
    ownership_df = pd.DataFrame(ownership_data)
    st.dataframe(ownership_df, use_container_width=True, hide_index=True)
    
elif not api_key:
    st.info("🔑 Please enter your FinancialModelingPrep (FMP) API key above to load safe, high-capacity stock records instantly.")
