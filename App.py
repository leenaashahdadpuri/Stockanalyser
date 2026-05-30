import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Custom Wall Street Analyst Dashboard")
st.write("Type any US stock ticker below to pull real-time analyst recommendations and company data.")

# 1. Text input field instead of a drop-down selection
# .strip().upper() cleans up spaces and forces uppercase formatting
user_input = st.text_input("Enter Stock Ticker (e.g., NVDA, AAPL, TSLA):", "NVDA")
selected_ticker = user_input.strip().upper()

# Only run the data pipeline if the user has typed something in
if selected_ticker:
    stock = yf.Ticker(selected_ticker)
    
    # --- Existing Data Fetching Block ---
    try:
        info = stock.info
        
        # If yfinance can't find a valid company name, the ticker likely doesn't exist
        if not info or "longName" not in info:
            st.error(f"Could not find any data for ticker '{selected_ticker}'. Please check the spelling and try again.")
            st.stop()
            
        company_name = info.get("longName", selected_ticker)
        summary = info.get("longBusinessSummary", "No description available.")
        current_rec = info.get("recommendationKey", "N/A").upper()
        target_price = info.get("targetMeanPrice", "N/A")
        current_price = info.get("currentPrice", "N/A")
    except Exception as e:
        st.error(f"Error retrieving data for '{selected_ticker}'. The ticker might be invalid or delisted.")
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
    
    # --- Upgrades and Downgrades Table ---
    st.subheader("🔄 Recent Analyst Upgrades & Downgrades")
    try:
        ud_df = stock.get_upgrades_downgrades()
        if ud_df is not None and not ud_df.empty:
            ud_df = ud_df.reset_index()
            ud_df.columns = ["Grade Date", "Firm", "To Grade", "From Grade", "Action"]
            ud_df["Grade Date"] = pd.to_datetime(ud_df["Grade Date"]).dt.date
            ud_df = ud_df.sort_values(by="Grade Date", ascending=False)
            st.dataframe(ud_df.head(10), use_container_width=True, hide_index=True)
        else:
            st.info("No recent upgrade/downgrade history available for this stock.")
    except Exception as e:
        st.write("Upgrades and downgrades history is temporarily unavailable.")

    st.markdown("---")
    
    # --- Institutional Investors Block ---
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
else:
    st.info("Please enter a stock ticker above to get started.")
