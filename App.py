import streamlit as st
import requests
import pandas as pd

# Set up a wide layout for a clean dashboard view
st.set_page_config(layout="wide")
st.title("📊 Enterprise Analytics & Cached Dashboard")
st.write("Optimized to preserve your free Alpha Vantage API call limits using memory caching.")

# Setup Input Fields for Ticker and API Key
col_input1, col_input2 = st.columns([1, 2])
with col_input1:
    user_input = st.text_input("Enter Stock Ticker:", "NVDA")
    selected_ticker = user_input.strip().upper()
with col_input2:
    api_key = st.text_input("Enter Alpha Vantage API Key:", type="password")

# --- NEW: Cached Data Fetcher Engine ---
# ttl=3600 means the app remembers data for 1 hour before asking Alpha Vantage again
@st.cache_data(ttl=3600, show_spinner="Fetching financial datasets from server...")
def fetch_stock_data(ticker, key):
    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={key}"
    quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={key}"
    history_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={key}"
    
    # Run the raw server queries
    o_res = requests.get(overview_url).json()
    q_res = requests.get(quote_url).json()
    h_res = requests.get(history_url).json()
    
    return o_res, q_res, h_res

# Run the cached engine only if parameters are typed out
if selected_ticker and api_key:
    
    # Call our cached function
    overview_res, quote_res, history_res = fetch_stock_data(selected_ticker, api_key)
    
    # Check if any request returned a throttle notice or api limit message
    if "Note" in overview_res or "Note" in quote_res or "Note" in history_res:
        st.error("⚠️ Alpha Vantage API Rate limit reached (5 calls/min, 25 calls/day). Please wait 60 seconds or try again later.")
        st.info("💡 Tip: Because we added caching, checking the same stock again will not count against your API limit!")
        st.stop()
        
    if not overview_res or "Name" not in overview_res:
        st.error(f"Could not load an asset profile for '{selected_ticker}'. Check the spelling or your API authorization.")
        st.stop()
        
    # Core Content Extractions
    company_name = overview_res.get("Name", selected_ticker)
    summary = overview_res.get("Description", "No description available.")
    target_price = overview_res.get("AnalystTargetPrice", "N/A")
    
    quote_data = quote_res.get("Global Quote", {})
    current_price = quote_data.get("05. price", "N/A")

    # --- Profile layout Header Blocks ---
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"{company_name} ({selected_ticker})")
        st.subheader("🏢 Company Summary")
        st.write(summary)
    with col2:
        st.subheader("📈 Core Pricing Information")
        st.metric(label="Current Rate / Share Price", value=f"${float(current_price):.2f}" if current_price != "N/A" else "N/A")
        st.metric(label="Wall Street Target Mean", value=f"${target_price}" if target_price != "N/A" else "N/A")
        
    st.markdown("---")

    # --- Timeline Performance Tracking Charts ---
    st.subheader("📈 Historical Growth Performance Tracking")
    
    time_series_key = "Time Series (Daily)"
    if time_series_key in history_res:
        raw_prices = history_res[time_series_key]
        price_df = pd.DataFrame.from_dict(raw_prices, orient='index')
        
        price_df.index = pd.to_datetime(price_df.index)
        price_df = price_df.rename(columns={"4. close": "Close Price"})
        price_df["Close Price"] = pd.to_numeric(price_df["Close Price"])
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
        st.info("Historical line aggregation maps are temporarily fetching blank rows or throttling limits.")

    st.markdown("---")
    
    # --- Top Investors & Major Asset Ownership Metrics ---
    st.subheader("🐋 Major Stakeholder & Corporate Ownership Breakdown")
    try:
        inst_shares = overview_res.get("PercentInstitutions", "N/A")
        insider_shares = overview_res.get("PercentInsiders", "N/A")
        
        ownership_data = {
            "Top Institutional Investor Allocation %": [f"{inst_shares}%" if inst_shares != "N/A" else "N/A"],
            "Corporate Insider Allocation %": [f"{insider_shares}%" if insider_shares != "N/A" else "N/A"],
            "Revenue Growth Metrics (Quarterly YOY)": [f"{overview_res.get('QuarterlyRevenueGrowthYOY', 'N/A')}%"],
            "Net Profit Margins (Trailing Twelve Months)": [f"{overview_res.get('ProfitMargin', 'N/A')}%"]
        }
        
        ownership_df = pd.DataFrame(ownership_data)
        st.dataframe(ownership_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.write("Ownership allocation metrics are currently experiencing connection drops.")
        
elif not api_key:
    st.info("🔑 Please enter your Alpha Vantage API key in the password input field above to query live analytical records.")
