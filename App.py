import streamlit as st
import yfinance as yf
import pandas as pd

# Set up a wide layout for a clean dashboard view
st.set_page_config(layout="wide")
st.title("📊 Custom Wall Street Analyst Dashboard")
st.write("Type any US stock ticker below to pull real-time data, company info, and market consensus.")

# 1. TEXT INPUT FIELD (Replaced the drop-down menu)
# Initializes with "NVDA" as the default placeholder value
user_input = st.text_input("Enter Stock Ticker:", "NVDA")

# .strip().upper() ensures " tsla " or "aapl" format perfectly to "TSLA" or "AAPL"
selected_ticker = user_input.strip().upper()

# Run the data pipeline only if the text field isn't empty
if selected_ticker:
    stock = yf.Ticker(selected_ticker)
    
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

    # Split the top section into two columns
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
    
    # --- Wall Street Analyst Consensus Breakdown ---
    st.subheader("📊 Wall Street Analyst Consensus Breakdown")
    try:
        consensus_data = {
            "Recommendation Rating (0.0 Strong Buy - 5.0 Sell)": [info.get("recommendationMean", "N/A")],
            "Number of Analysts Tracking": [info.get("numberOfAnalystOpinions", "N/A")],
            "Target High Price": [f"${info.get('targetHighPrice', 'N/A')}"],
            "Target Low Price": [f"${info.get('targetLowPrice', 'N/A')}"],
            "Target Median Price": [f"${info.get('targetMedianPrice', 'N/A')}"]
        }
        
        consensus_df = pd.DataFrame(consensus_data)
        st.dataframe(consensus_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.write("Detailed consensus breakdown is temporarily unavailable.")

    st.markdown("---")
    
    # --- Institutional & Insider Ownership Breakdown ---
    st.subheader("🐋 Institutional & Insider Ownership")
    try:
        # Pull ownership stakes safely from the working .info dataset
        inst_pct = info.get('heldPercentInstitutions')
        insider_pct = info.get('heldPercentInsiders')
        
        # Format percentages safely in case values are None
        inst_str = f"{round(inst_pct * 100, 2)}%" if inst_pct is not None else "N/A"
        insider_str = f"{round(insider_pct * 100, 2)}%" if insider_pct is not None else "N/A"
        
        ownership_data = {
            "Institutions Holding Shares": [inst_str],
            "Insiders Holding Shares": [insider_str],
            "Shares Short (Current Month)": [f"{info.get('sharesShort', 'N/A'):,}" if isinstance(info.get('sharesShort'), (int, float)) else "N/A"],
            "Short Ratio (Days to Cover)":
