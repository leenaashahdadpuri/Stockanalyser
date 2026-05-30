import streamlit as st
import requests
import pandas as pd
import datetime

# Set up a wide layout for a clean dashboard view
st.set_page_config(layout="wide")
st.title("📊 Open Financial Analytics Dashboard")
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
    # Core Endpoint 1: Active profile metrics
    profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={token}"
    # Core Endpoint 2: Real-time market valuation rates
    quote_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={token}"
    # Core Endpoint 3: Real-time Analyst Recommendation trends
    rec_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={ticker}&token={token}"
    
    # Core Endpoint 4: Top News headlines (Trailing 7 days)
    today = datetime.date.today().strftime('%Y-%m-%d')
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    news_url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={week_ago}&to={today}&token={token}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        p_res = requests.get(profile_url, headers=headers).json()
        q_res = requests.get(quote_url, headers=headers).json()
        r_res = requests.get(rec_url, headers=headers).json()
        n_res = requests.get(news_url, headers=headers).json()
        return p_res, q_res, r_res, n_res
    except Exception as e:
        return None, None, None, None

# Launch data engine only when user fills both boxes
if selected_ticker and api_token:
    profile_res, quote_res, rec_res, news_res = fetch_finnhub_data(selected_ticker, api_token)
    
    # Validate token authentication responses
    if not profile_res or "name" not in profile_res:
        st.error(f"⚠️ Could not pull profiles for '{selected_ticker}'.")
        st.info("💡 Confirm your Finnhub token was copied completely without trailing spaces.")
        st.stop()
        
    # Content Variable Extractions
    company_name = profile_res.get("name", selected_ticker)
    industry = profile_res.get("finnhubIndustry", "N/A")
    mkt_cap = profile_res.get("marketCapitalization", 0.0)
    shares_outstanding = profile_res.get("shareOutstanding", 0.0)
    
    current_price = quote_res.get("c", 0.0)
    previous_close = quote_res.get("pc", 0.0)
    price_change = current_price - previous_close
    
    # Display Layout Top Headline Bar
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"{company_name} ({selected_ticker})")
        st.subheader(f"🏢 Sector Category: {industry}")
    with col2:
        st.metric(label="Current Share Price", value=f"${current_price:,.2f}", delta=f"{price_change:+.2f}")
            
    st.markdown("---")
    
    # ==================== THE 3 NEW EXPLICIT SECTIONS ====================
    
    # --- SECTION 1: WHAT THE COMPANY DOES & STAKEHOLDER STRUCTURE ---
    st.header("1. 🏢 Business Operations & Capital Structure")
    
    # Check if a custom landing page or ticker description is available from Finnhub profile metadata
    web_url = profile_res.get("weburl", "N/A")
    exchange = profile_res.get("exchange", "N/A")
    ipo_date = profile_res.get("ipo", "N/A")
    
    st.write(f"**{company_name}** operates as a major company within the **{industry}** sector. The equity is listed primarily on the **{exchange}** exchange network,
