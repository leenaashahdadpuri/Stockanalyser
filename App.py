import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Social Trends & Wall Street Analyst Dashboard")

social_trending_stocks = ["NVDA", "TSLA", "AAPL", "AMD", "MSFT"]
selected_ticker = st.sidebar.selectbox("Select a Trending Stock to Inspect", social_trending_stocks)

if selected_ticker:
    stock = yf.Ticker(selected_ticker)
    
    # --- Existing Data Fetching Block ---
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

    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"{company_name} ({selected_ticker})")
        st.subheader("🏢 What the Company Does")
        st.write(summary)
    with col2:
        st.subheader("📈 Analyst Recommendation")
        st.metric(label="Wall Street Rating", value=current_rec)
        st.metric(label="Current Price", value=f"${current_price}")
        st.metric(label="Analyst Target Price", value=f"${target_price}")

    st.markdown("---")
    
    # --- NEW: Upgrades and Downgrades Table ---
    st.subheader("🔄 Recent Analyst Upgrades & Downgrades")
    try:
        # Fetch the dataframe from yfinance
        ud_df = stock.get_upgrades_downgrades()
        
        if ud_df is not None and not ud_df.empty:
            # Reset index so 'Grade Date' becomes a regular visible column
            ud_df = ud_df.reset_index()
            
            # Clean up the column names for a polished display
            ud_df.columns = ["Grade Date", "Firm", "To Grade", "From Grade", "Action"]
            
            # Convert date column to a clean date format (removing timezone/hours)
            ud_df["Grade Date"] = pd.to_datetime(ud_df["Grade Date"]).dt.date
            
            # Sort with the newest analyst actions at the very top
            ud_df = ud_df.sort_values(by="Grade Date", ascending=False)
            
            # Display the top 10 most recent updates
            st.dataframe(ud_df.head(10), use_container_width=True, hide_index=True)
        else:
            st.info("No recent upgrade/downgrade history available for this stock.")
    except Exception as e:
        st.write("Upgrades and downgrades history is temporarily unavailable.")

    st.markdown("---")
    
    # --- Existing Institutional Investors Block ---
    st.subheader("🐋 Top 5 Institutional Investors")
    try:
        holders_df = stock.institutional_holders
        if holders_df is not None and not holders_df.empty:
            holders_df.columns = ["Holder Name", "Shares Owned", "Date Reported", "% Out", "Total Value"]
            st.dataframe(holders_df.head(5), use_container_width=True)
        else:
            st.write("No institutional holder data found.")
    except:
        st.write("Institutional investors currently unavailable.")
