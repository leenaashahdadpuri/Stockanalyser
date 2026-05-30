# --- FIXED: Reliable Ownership Breakdown ---
    st.subheader("🐋 Institutional & Insider Ownership")
    try:
        # Pulling the raw ownership stakes directly from the working .info dictionary
        ownership_data = {
            "Institutions Holding Shares": [f"{round(info.get('heldPercentInstitutions', 0) * 100, 2)}%"],
            "Insiders Holding Shares": [f"{round(info.get('heldPercentInsiders', 0) * 100, 2)}%"],
            "Shares Short (Current Month)": [f"{info.get('sharesShort', 'N/A'):,}" if isinstance(info.get('sharesShort'), (int, float)) else "N/A"],
            "Short Ratio (Days to Cover)": [info.get('shortRatio', 'N/A')]
        }
        
        # Turn it into a clean, horizontal summary table
        ownership_df = pd.DataFrame(ownership_data)
        st.dataframe(ownership_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.write("Ownership and investor breakdown is temporarily unavailable.")
