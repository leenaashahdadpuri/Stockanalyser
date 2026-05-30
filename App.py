import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Custom Wall Street Analyst Dashboard")
st.write("Type any US stock ticker below to pull real-time analyst recommendations and company data.")

user_input = st.text_input("Enter Stock Ticker (e.g., NVDA, AAPL, TSLA):", "NVDA")
selected_ticker = user_input.strip().upper()

if selected_ticker:
    stock = yf.Ticker(selected_ticker)
    
    try:
        info = stock.info
        if not info or "longName" not in info:
            st.error(f"Could not find any data for ticker '{selected_ticker}'. Please check the spelling.")
            st.stop()
            
        company_name = info.get("longName", selected_ticker)
        summary = info.get("longBusinessSummary", "No description available.")
        current_rec = info.get("recommendationKey", "N/A").upper()
        target_price = info.get("targetMeanPrice", "N/A")
        current_price = info.get("currentPrice", "N/A")
    except Exception as e:
        st.error(f"Error retrieving data for '{selected_ticker}'.")
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
    
    # --- FIXED: Reliable Analyst Consensus Breakdown ---
    st.subheader("📊 Wall Street Analyst Consensus Breakdown")
    try:
        # Pulling the raw breakdown directly from the working .info dictionary
        consensus_data = {
            "Recommendation Rating (0.0 Strong Buy - 5.0 Sell)": [info.get("recommendationMean", "N/A")],
            "Number of Analysts Tracking": [info.get("numberOfAnalystOpinions", "N/A")],
            "Target High Price": [f"${info.get('targetHighPrice', 'N/A')}"],
            "Target Low Price": [f"${info.get('targetLowPrice', 'N/A')}"],
            "Target Median Price": [f"${info.get('targetMedianPrice', 'N/A')}"]
        }
        
        # Turn it into a clean, horizontal summary table
        consensus_df = pd.DataFrame(consensus_data)
        st.dataframe(consensus_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.write("Detailed consensus breakdown is temporarily unavailable.")

    st.markdown("---")
    
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
