import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from src.stats_engine import get_all_time_player_stats, get_all_opponents
from utils.ui import add_rcb_theme, show_banner

st.set_page_config(page_title="RCB Analytics Dashboard", layout="wide")
add_rcb_theme()

# --- CSS OVERRIDE FOR DROPDOWNS READABILITY & SCROLLABLE MAX HEIGHT ---
st.markdown(
    """
    <style>
    /* Ensure placeholder text in the main box is white */
    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }
    
    /* Force all text/team names inside the popup menu to be brilliant white */
    div[data-baseweb="popover"] *, 
    ul[data-baseweb="menu"] *, 
    div[data-baseweb="menu"] * {
        color: #ffffff !important;
    }
    
    /* Set popup container background to match your dark theme cleanly */
    div[data-baseweb="popover"], ul[data-baseweb="menu"] {
        background-color: #0e1117 !important;
        max-height: 250px !important;
        overflow-y: auto !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. SESSION STATE PERSISTENCE ---
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["All Time Stats", "Team Analysis"], key="nav_radio")
show_banner()

# --- 1. INPUT BATCHING (ST.FORM & OUT-OF-FORM MULTISELECT) ---
st.sidebar.subheader("Filters")
opponent_filter = st.sidebar.multiselect("Filter by Opponent:", get_all_opponents())

with st.sidebar.form(key='filter_form'):
    phase_filter = st.selectbox("Filter by Phase:", ["Overall", "Powerplay", "Middle", "Death"])
    submit_button = st.form_submit_button(label='Apply Filters')

# Update state based on form submission
phase_val = phase_filter if phase_filter != "Overall" else None
selected_opp = opponent_filter[0] if opponent_filter else None

base_dir = os.path.dirname(os.path.abspath(__file__))
master_stats_path = os.path.join(base_dir, "data", "master_stats.csv")
team_stats_path = os.path.join(base_dir, "data", "team_stats_data.json")

if page == "All Time Stats":
    st.title("All-Time Player Statistics")
    if os.path.exists(master_stats_path):
        df = pd.read_csv(master_stats_path)
        # Use session state for persistence
        selected_player = st.selectbox("Search for a player:", df['player_name'].unique().tolist(), 
                                       index=None, key="player_select")
        
        if selected_player:
            stats = get_all_time_player_stats(selected_player, opponent_filter=selected_opp, phase=phase_val)
            st.subheader(f"Stats for {selected_player}")
            
            # --- 2. KPI SCORECARDS WITH DELTAS ---
            c1, c2, c3, c4, c5 = st.columns(5)
            # Delta compares current avg to a baseline of 30.0
            c1.metric("Runs", int(stats['batting']['runs']), delta=f"{stats['batting']['average'] - 30.0:.1f}")
            c2.metric("Avg", stats['batting']['average'])
            c3.metric("SR", stats['batting']['strike_rate'])
            c4.metric("Sixes", int(stats['batting']['sixes']))
            c5.metric("Fours", int(stats['batting']['fours']))
            
            st.subheader("Bowling Performance")
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Wickets", int(stats['bowling']['wickets']))
            b2.metric("Economy", stats['bowling']['economy'])
            b3.metric("Avg", stats['bowling']['avg'])
            b4.metric("SR", stats['bowling']['sr'])
        
        # --- FIXED TREND ANALYSIS BLOCK ---
        st.divider()
        st.subheader(f"Performance Trends for {selected_player}")
        trend_csv = os.path.join(base_dir, "data", "player_opponent_stats.csv")
        
        if selected_player and os.path.exists(trend_csv):
            df_trend = pd.read_csv(trend_csv)
            if 'phase' in df_trend.columns:
                df_trend = df_trend[df_trend['phase'] == phase_filter]
            player_trends = df_trend[df_trend['player_name'] == selected_player].groupby('season').sum(numeric_only=True).reset_index()
            metric = st.selectbox("Select Metric to View:", ["runs", "sixes", "wickets"])
            
            if not player_trends.empty:
                fig = px.line(player_trends, x="season", y=metric, title=f"{selected_player} - {metric.capitalize()} per Season", markers=True, template="plotly_dark")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader("Head-to-Head Comparison")
        col_a, col_b = st.columns(2)
        p1 = col_a.selectbox("Player 1:", df['player_name'].unique().tolist(), index=None, key="p1")
        p2 = col_b.selectbox("Player 2:", df['player_name'].unique().tolist(), index=None, key="p2")
        
        if p1 and p2:
            s1 = get_all_time_player_stats(p1, opponent_filter=selected_opp, phase=phase_val)
            s2 = get_all_time_player_stats(p2, opponent_filter=selected_opp, phase=phase_val)
            
            data = {
                "Metric": ["Runs", "Bat Avg", "Bat SR", "Sixes", "Wickets", "Econ", "Bowl Avg"],
                p1: [int(s1['batting']['runs']), s1['batting']['average'], s1['batting']['strike_rate'], int(s1['batting']['sixes']), int(s1['bowling']['wickets']), s1['bowling']['economy'], s1['bowling']['avg']],
                p2: [int(s2['batting']['runs']), s2['batting']['average'], s2['batting']['strike_rate'], int(s2['batting']['sixes']), int(s2['bowling']['wickets']), s2['bowling']['economy'], s2['bowling']['avg']]
            }
            
            df_comp = pd.DataFrame(data).set_index("Metric")
            def highlight_max(row):
                if row.name in ['Econ', 'Bowl Avg']: is_better = row == row.min()
                else: is_better = row == row.max()
                # Soft transparent green preventing text washout
                return ['background-color: rgba(46, 139, 87, 0.3); color: #ffffff;' if v else '' for v in is_better]
            
            st.dataframe(df_comp.style.apply(highlight_max, axis=1).format(precision=2), use_container_width=True)
            
elif page == "Team Analysis":
    st.title("RCB Team Analysis")
    if os.path.exists(team_stats_path):
        with open(team_stats_path, "r") as f: t_data = json.load(f)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Overall Record")
            fig = px.pie(values=[t_data["overall"]["wins"], t_data["overall"]["losses"]], names=['Wins', 'Losses'])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='white'))
            st.plotly_chart(fig)
        with col2:
            season = st.selectbox("Select Season", sorted(t_data["seasons"].keys(), reverse=True))
            st.subheader(f"Record for {season}")
            s_data = t_data["seasons"][season]
            fig_s = px.pie(values=[s_data["wins"], s_data["losses"]], names=['Wins', 'Losses'])
            fig_s.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='white'))
            st.plotly_chart(fig_s)
        st.subheader("Man of the Match Leaders (All Time)")
        mom_all = pd.DataFrame(list(t_data["overall"]["mom"].items()), columns=['Player', 'Awards'])
        st.table(mom_all.sort_values('Awards', ascending=False).head(5))
        st.subheader(f"Man of the Match Leaders ({season})")
        season_mom_data = t_data["seasons"][season].get("mom", {})
        if season_mom_data:
            mom_season = pd.DataFrame(list(season_mom_data.items()), columns=['Player', 'Awards'])
            st.table(mom_season.sort_values('Awards', ascending=False).head(5))
        else: st.write(f"No MOM data found for {season}.")