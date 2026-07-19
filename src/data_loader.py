import pandas as pd
import os
import glob
import json
import streamlit as st

# Your verified data location
DATA_DIR = r"C:\projects_data\data\all_ipl_matches.json"

def normalize_team_name(team_name):
    """Standardizes franchise names to ensure consistent historical stats."""
    name_map = {
        "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
        "Royal Challengers Bengaluru": "Royal Challengers Bengaluru"
    }
    return name_map.get(team_name, team_name)

@st.cache_data
def load_data():
    """Loads all JSON files, normalizes team names, and filters for RCB."""
    files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    
    if not files:
        print("No files found in directory.")
        return None
    
    df_list = []
    
    for f in files:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                match_info = data.get('info', {})
                
                # Normalize team names in the info section
                raw_teams = match_info.get('teams', [])
                normalized_teams = [normalize_team_name(t) for t in raw_teams]
                
                # Check for RCB existence after normalization
                if "Royal Challengers Bengaluru" in normalized_teams:
                    # Flattening the info for the dataframe
                    df = pd.json_normalize(match_info)
                    
                    # Store normalized teams for filtering in the app
                    df['teams_normalized'] = [normalized_teams]
                    df['match_id'] = os.path.basename(f)
                    df_list.append(df)
                    
        except Exception as e:
            # Skip corrupted files
            continue
            
    if not df_list:
        return None
        
    return pd.concat(df_list, ignore_index=True)