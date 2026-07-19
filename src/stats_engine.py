import os
import json
import glob
import streamlit as st

def get_phase(over_num):
    if over_num < 6: return "Powerplay"
    if over_num < 15: return "Middle"
    return "Death"

def get_player_batting_stats(data, player_name, phase=None):
    runs, balls, fours, sixes, dismissals = 0, 0, 0, 0, 0
    for inning in data.get('innings', []):
        for over in inning.get('overs', []):
            over_num = int(over.get('over', 0))
            if phase and get_phase(over_num) != phase: continue
            for delivery in over.get('deliveries', []):
                if delivery.get('batter') == player_name:
                    runs_scored = delivery.get('runs', {}).get('batter', 0)
                    runs += runs_scored
                    balls += 1
                    if runs_scored == 4: fours += 1
                    if runs_scored == 6: sixes += 1
                for wicket in delivery.get('wickets', []):
                    if wicket.get('player_out') == player_name:
                        dismissals += 1
    return {"runs": runs, "balls": balls, "fours": fours, "sixes": sixes, "dismissals": dismissals}

def get_player_bowling_stats(data, player_name, phase=None):
    runs_conceded, balls_bowled, wickets = 0, 0, 0
    target = player_name.strip()
    for inning in data.get('innings', []):
        for over in inning.get('overs', []):
            over_num = int(over.get('over', 0))
            if phase and get_phase(over_num) != phase: continue
            for delivery in over.get('deliveries', []):
                if str(delivery.get('bowler', '')).strip() == target:
                    balls_bowled += 1
                    runs_conceded += delivery.get('runs', {}).get('total', 0)
                    for w in delivery.get('wickets', []):
                        if w.get('kind') not in ['run out', 'retired hurt', 'obstructing the field']:
                            wickets += 1
    return {"runs_conceded": runs_conceded, "balls_bowled": balls_bowled, "wickets": wickets}

@st.cache_data
def get_all_opponents(data_dir=None):
    if data_dir is None: data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    files = glob.glob(os.path.join(data_dir, "*.json"))
    opponents = set()
    for f in files:
        with open(f, 'r') as file:
            match_data = json.load(file)
            for t in match_data.get('info', {}).get('teams', []):
                if t != "Royal Challengers Bengaluru": opponents.add(t)
    return sorted(list(opponents))

@st.cache_data
def get_all_time_player_stats(player_name, data_dir=None, opponent_filter=None, phase=None):
    if data_dir is None: data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    b_totals = {"runs": 0, "balls": 0, "fours": 0, "sixes": 0, "dismissals": 0}
    bl_totals = {"runs_conceded": 0, "balls_bowled": 0, "wickets": 0}
    for f in glob.glob(os.path.join(data_dir, "*.json")):
        with open(f, 'r') as file:
            data = json.load(file)
            players_map = data.get('info', {}).get('players', {})
            player_team = next((team for team, players in players_map.items() if player_name in players), None)
            if not player_team: continue
            opponent = next((t for t in data.get('info', {}).get('teams', []) if t != player_team), None)
            if opponent_filter and opponent != opponent_filter: continue
            
            b = get_player_batting_stats(data, player_name, phase)
            for k in b_totals: b_totals[k] += b.get(k, 0)
            bl = get_player_bowling_stats(data, player_name, phase)
            for k in bl_totals: bl_totals[k] += bl.get(k, 0)
            
    bat_avg = (b_totals['runs'] / b_totals['dismissals']) if b_totals['dismissals'] > 0 else b_totals['runs']
    bat_sr = (b_totals['runs'] / b_totals['balls'] * 100) if b_totals['balls'] > 0 else 0
    bowl_eco = (bl_totals['runs_conceded'] / (bl_totals['balls_bowled'] / 6)) if bl_totals['balls_bowled'] > 0 else 0
    bowl_avg = (bl_totals['runs_conceded'] / bl_totals['wickets']) if bl_totals['wickets'] > 0 else 0
    bowl_sr = (bl_totals['balls_bowled'] / bl_totals['wickets']) if bl_totals['wickets'] > 0 else 0
    return {
        "batting": {**b_totals, "average": round(bat_avg, 2), "strike_rate": round(bat_sr, 2)},
        "bowling": {**bl_totals, "economy": round(bowl_eco, 2), "avg": round(bowl_avg, 2), "sr": round(bowl_sr, 2)}
    }