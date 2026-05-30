import streamlit as st
import requests
import pandas as pd

# Set up a wide layout for a clean dashboard view
st.set_page_config(layout="wide")
st.title("📊 Reliable Wall Street Analyst Dashboard")
st.write("Powered by Alpha Vantage API (Bypasses Yahoo Cloud Blocking Blocks)")

# 1. Setup Input Fields for Ticker and API Key
col_input1, col_input2 = st.columns([1, 2])
with col_input1:
    user_input = st.text_input("Enter Stock Ticker:", "NVDA")
    selected_ticker = user_input.strip().upper()
with col_input2:
    # It's best practice to put your key here so the cloud doesn't block you
    api_key = st.text_input("Enter Alpha Vantage API Key:", type="password")

# Run only if the ticker and API key are provided
if selected_ticker and api_key:
    
    # URL 1: Fetch Company Overview & Fundamentals
    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={selected_ticker}&apikey={api_key}"
    
    # URL 2: Fetch Current Stock Price Quote
    quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={selected_ticker}&apikey={api_key}"
    
    try:
        overview_res = requests.get(overview_url).json()
        quote_res = requests.get(quote_url).json()
        
        # Check if the API returned an error or an empty note
        if "Note" in overview_res or "Note" in quote_res:
            st.warning("⚠️ Standard API Rate limit reached (Max 5 requests per minute). Please wait 60 seconds and try again.")
            st.stop()
            
        if not overview_res or "Name" not in overview_res:
            st.error(f"Could not find data for '{selected_ticker}'. Please verify the ticker or your API key.")
            st.stop()
            
        # Extract Variables from JSON response safely
        company_name = overview_res.get("Name", selected_ticker)
        summary = overview_res.get("Description", "No description available.")
        analyst_rating = overview_res.get("AnalystRatingStrongBuy", "N/A") # Alternative sentiment tracker
        target_price = overview_res.get("AnalystTargetPrice", "N/A")
        
        # Extract current price safely from the Quote API response dictionary
        quote_data = quote_res.get("Global Quote", {})
        current_price = quote_data.get("05. price", "N/A")
        
    except Exception as e:
        st.error("Error communicating with the data servers. Please verify your connection setup.")
        st.stop()

    # Split display content into layout columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"{company_name} ({selected_ticker})")
        st.subheader("🏢 What the Company Does")
        st.write(summary)
        
    with col2:
        st.subheader("📈 Analyst Recommendation")
        st.metric(label="Analyst Target Price", value=f"${target_price}" if target_price != "N/A" else "N/A")
        st.metric(label="Current Stock Price", value=f"${float(current_price):.2f}" if current_price != "N/A" else "N/A")
        
    st.markdown("---")
    
    # --- Wall Street Valuation & Growth Metrics ---
    st.subheader("📊 Fundamental Valuation Breakdown")
    try:
        valuation_data = {
            "PE Ratio": [overview_res.get("PERatio", "N/A")],
            "PEG Ratio": [overview_res.get("PEGRatio", "N/A")],
            "Price To Book Ratio": [overview_res.get("PriceToBookRatio", "N/A")],
            "EV To Revenue": [overview_res.get("EVToRevenue", "N/A")],
            "52 Week High": [f"${overview_res.get('52WeekHigh', 'N/A')}"],
            "52 Week Low": [f"${overview_res.get('52WeekLow', 'N/A')}"]
        }
        
        val_df = pd.DataFrame(valuation_data)
        st.dataframe(val_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.write("Valuation breakdown metrics are currently unavailable.")

    st.markdown("---")
    
    # --- Major Institutional & Stakeholder Metrics ---
    st.subheader("🐋 Major Stakeholder Allocation Overview")
    try:
        # Alpha Vantage separates ownership values cleanly in the overview dictionary
        inst_shares = overview_res.get("PercentInstitutions", "N/A")
        insider_shares = overview_res.get("PercentInsiders", "N/A")
        
        ownership_data = {
            "Institutions Holding Shares": [f"{inst_shares}%" if inst_shares != "N/A" else "N/A"],
            "Insiders Holding Shares": [f"{insider_shares}%" if insider_shares != "N/A" else "N/A"],
            "Quarterly Earnings Growth (YOY)": [f"{overview_res.get('QuarterlyEarningsGrowthYOY', 'N/A')}%"],
            "Quarterly Revenue Growth (YOY)": [f"{overview_res.get('QuarterlyRevenueGrowthYOY', 'N/A')}%"]
        }
        
        ownership_df = pd.DataFrame(ownership_data)
        st.dataframe(ownership_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.write("Ownership allocation statistics are currently unavailable.")
        
elif not api_key:
    st.info("🔑 Please enter your Alpha Vantage API key in the input box above to load stock metrics safely.")
