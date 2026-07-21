import streamlit as st
import os
from src.stats_engine import get_all_time_player_stats

st.title("Stats Engine Debugger")

# --- FIX: Dynamic Path Calculation ---
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data")
# --------------------------------------

player_name = st.text_input("Enter Player Name:", "Virat Kohli")

if st.button("Run Test"):
    st.write(f"Searching for data in: {data_path}")
    
    # This function uses the path configured inside your src/stats_engine.py
    stats = get_all_time_player_stats(player_name)
    
    st.subheader("Engine Output")
    st.write(f"Matches Processed: {stats.get('meta', {}).get('files_processed')}")
    st.json(stats)

    if stats.get('batting', {}).get('runs') == 0:
        st.error("Stats returned 0. Ensure the player name matches the JSON exactly (e.g., 'Virat Kohli').")