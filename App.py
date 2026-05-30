import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Social Trends & Wall Street Analyst Dashboard")
st.write("Tracking top social media favorites alongside Wall Street consensus.")

# 1. Social-Media popular stocks list to scan
# In a production app, you can hook this up to a free Reddit API or scrape stocktwits
social_trending_stocks = ["NVDA", "TSLA", "AAPL", "AMD", "MSFT"]

# 2. Sidebar to select from the top trending stocks
selected_ticker = st.sidebar.selectbox("Select a Trending Stock to Inspect", social_trending_stocks)

if selected_ticker:
    stock = yf.Ticker(selected_ticker)
    
    # Fetch safe data blocks using try/except blocks in case data is blank
    try:
        info = stock.info
        company_name = info.get("longName", selected_ticker)
        summary = info.get("longBusinessSummary", "No description available.")
        current_rec = info.get("recommendationKey", "N/A").upper()
        target_price = info.get("targetMeanPrice", "N/A")
        current_price = info.get("currentPrice", "N/A")
    except:
        st.error("Error retrieving core stock information.")
        st.stop()

    # Layout with columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header(f"{company_name} ({selected_ticker})")
        st.subheader("🏢 What the Company Does")
        st.write(summary)

    with col2:
        st.subheader("📈 Analyst Recommendation")
        
        # Display recommendation card
        st.metric(label="Wall Street Rating", value=current_rec)
        st.metric(label="Current Price", value=f"${current_price}")
        st.metric(label="Analyst Target Price", value=f"${target_price}")

    st.markdown("---")
    
    # 3. Pull Top Investors (Institutional Holders)
    st.subheader("🐋 Top 5 Institutional Investors")
    try:
        holders_df = stock.institutional_holders
        if holders_df is not None and not holders_df.empty:
            # Clean up dataframe columns for standard viewing
            holders_df.columns = ["Holder Name", "Shares Owned", "Date Reported", "% Out", "Total Value"]
            st.dataframe(holders_df.head(5), use_container_width=True)
        else:
            st.write("No institutional holder data found.")
    except:
        st.write("Institutional investors currently unavailable for this ticker.")
