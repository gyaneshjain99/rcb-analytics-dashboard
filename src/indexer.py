import os
import json
import glob
import pandas as pd
from stats_engine import get_player_batting_stats, get_player_bowling_stats

# Define both names to ensure all-time coverage
RCB_NAMES = ["Royal Challengers Bengaluru", "Royal Challengers Bangalore"]

def run_indexer():
    base_dir = r"C:\Users\gyane\OneDrive\Desktop\rcb-analytics-dashboard"
    files = glob.glob(os.path.join(base_dir, "data", "*.json"))
    player_totals = {}
    
    for f in files:
        with open(f, 'r') as file:
            try:
                data = json.load(file)
                players_rosters = data.get('info', {}).get('players', {})
                for roster in players_rosters.values():
                    for player in roster:
                        if player not in player_totals:
                            player_totals[player] = {'runs': 0, 'balls': 0, 'dismissals': 0, 'sixes': 0, 'fours': 0, 'wickets': 0, 'runs_conceded': 0, 'balls_bowled': 0}
                        
                        b = get_player_batting_stats(data, player)
                        bl = get_player_bowling_stats(data, player)
                        
                        player_totals[player]['runs'] += b.get('runs', 0)
                        player_totals[player]['balls'] += b.get('balls', 0)
                        player_totals[player]['dismissals'] += b.get('dismissals', 0)
                        player_totals[player]['sixes'] += b.get('sixes', 0)
                        player_totals[player]['fours'] += b.get('fours', 0)
                        player_totals[player]['wickets'] += bl.get('wickets', 0)
                        player_totals[player]['runs_conceded'] += bl.get('runs_conceded', 0)
                        player_totals[player]['balls_bowled'] += bl.get('balls_bowled', 0)
            except Exception:
                continue
                
    df = pd.DataFrame.from_dict(player_totals, orient='index').reset_index().rename(columns={'index': 'player_name'})
    df.to_csv(os.path.join(base_dir, "data", "master_stats.csv"), index=False)
    print(f"Indexing complete. Processed {len(files)} matches.")

if __name__ == "__main__":
    run_indexer()