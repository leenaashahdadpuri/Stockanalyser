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
    
    # ==================== THE 3 EXPLICIT SECTIONS ====================
    
    # --- SECTION 1: WHAT THE COMPANY DOES & STAKEHOLDER STRUCTURE ---
    st.header("1. 🏢 Business Operations & Capital Structure")
    
    web_url = profile_res.get("weburl", "N/A")
    exchange = profile_res.get("exchange", "N/A")
    ipo_date = profile_res.get("ipo", "N/A")
    
    # FIXED: Replaced single quotes with triple quotes to cleanly support multiline text block outputs
    st.write(f"""
    **{company_name}** operates as a major enterprise within the **{industry}** market space. 
    The company equity is listed primarily on the **{exchange}** exchange network, tracking public trading 
    records since its initial market debut on **{ipo_date}**.
    """)
    st.write(f"🌐 **Official Corporate Portal:** [{web_url}]({web_url})")
    
    # Capital structure context block
    st.subheader("🐋 Market Foothold & Share Allocation Summary")
    ownership_data = {
        "Market Capitalization Valuation": [f"${mkt_cap:,.2f} Million"],
        "Total Shares Outstanding": [f"{shares_outstanding:,.2f}M Shares"],
        "Reporting Currency Code": [profile_res.get("currency", "USD")],
        "Base Corporate Region": [profile_res.get("country", "US")]
    }
    st.dataframe(pd.DataFrame(ownership_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # --- SECTION 2: BUY OR SELL RECOMMENDATION BREAKDOWN ---
    st.header("2. 📊 Wall Street Recommendation Trends")
    
    if isinstance(rec_res, list) and len(rec_res) > 0:
        latest_rec = rec_res[0]
        period = latest_rec.get("period", "Current")
        
        strong_buy = latest_rec.get("strongBuy", 0)
        buy = latest_rec.get("buy", 0)
        hold = latest_rec.get("hold", 0)
        sell = latest_rec.get("sell", 0)
        strong_sell = latest_rec.get("strongSell", 0)
        
        st.write(f"Consensus metrics tracking Wall Street analyst targets for the statement cycle (**{period}**):")
        
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        m_col1.metric("🟢 Strong Buy", strong_buy)
        m_col2.metric("🌱 Buy", buy)
        m_col3.metric("🟡 Hold", hold)
        m_col4.metric("🚨 Sell", sell)
        m_col5.metric("❌ Strong Sell", strong_sell)
        
        rec_chart_data = pd.DataFrame({
            "Rating Class": ["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"],
            "Analyst Vote Counts": [strong_buy, buy, hold, sell, strong_sell]
        }).set_index("Rating Class")
        st.bar_chart(rec_chart_data)
    else:
        st.info("Analyst consensus targets are clearing cache channels for this ticker.")
        
    st.markdown("---")
    
    # --- SECTION 3: TOP NEWS / LATEST UPDATES ---
    st.header("3. 📰 Latest Corporate Headlines & Market Updates")
    
    if isinstance(news_res, list) and len(news_res) > 0:
        for article in news_res[:5]:
            headline = article.get("headline", "No Headline Available")
            source = article.get("source", "Market News")
            summary_text = article.get("summary", "")
            url = article.get("url", "#")
            
            st.subheader(f"• {headline}")
            st.caption(f"Source: **{source}**")
            if summary_text:
                st.write(summary_text)
            st.markdown(f"🔗 [Read Full Coverage]({url})")
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No mainstream headlines published for this ticker over the trailing 7 days.")
        
elif not api_token:
    st.info("🔑 Please enter your Finnhub API Token above to boot your live tracking analytics framework.")
