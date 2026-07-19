import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, glob, pandas as pd
from src.stats_engine import get_player_batting_stats, get_player_bowling_stats, get_phase

def precompute_data():
    all_rows = []
    for f in glob.glob("data/*.json"):
        with open(f, 'r') as file:
            data = json.load(file)
            season = data.get('info', {}).get('season', 'Unknown')
            # Extract players mapping correctly
            player_dict = data.get('info', {}).get('players', {})
            all_players = set()
            for team_players in player_dict.values(): all_players.update(team_players)
            
            for player in all_players:
                # Calculate for overall (None) and specific phases
                for phase in [None, "Powerplay", "Middle", "Death"]:
                    b = get_player_batting_stats(data, player, phase)
                    bl = get_player_bowling_stats(data, player, phase)
                    row = {"player_name": player, "season": season, "phase": phase or "Overall", **b, **bl}
                    all_rows.append(row)
    pd.DataFrame(all_rows).to_csv("data/player_opponent_stats.csv", index=False)
    print("Pre-computation complete.")

if __name__ == "__main__": precompute_data()