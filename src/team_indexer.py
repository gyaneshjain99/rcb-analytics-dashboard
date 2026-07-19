import os
import json
import glob

RCB_NAMES = ["Royal Challengers Bengaluru", "Royal Challengers Bangalore"]

def run_team_indexer():
    base_dir = r"C:\Users\gyane\OneDrive\Desktop\rcb-analytics-dashboard"
    files = glob.glob(os.path.join(base_dir, "data", "*.json"))
    
    # Structure: overall totals, seasons breakdown, and RCB-roster filtered MOM
    team_data = {"overall": {"wins": 0, "losses": 0, "mom": {}}, "seasons": {}}
    
    for f in files:
        with open(f, 'r') as file:
            try:
                data = json.load(file)
                info = data.get('info', {})
                teams = info.get('teams', [])
                
                # Robust season extraction: check info.season, then info.dates
                season = str(info.get('season', 'Unknown'))
                if season == 'Unknown' and 'dates' in info:
                    season = str(info['dates'][0].split('-')[0])
                
                # Check if RCB is involved
                if any(name in teams for name in RCB_NAMES):
                    if season not in team_data["seasons"]:
                        team_data["seasons"][season] = {"wins": 0, "losses": 0, "mom": {}}
                    
                    winner = info.get('outcome', {}).get('winner')
                    if winner in RCB_NAMES:
                        team_data["overall"]["wins"] += 1
                        team_data["seasons"][season]["wins"] += 1
                    else:
                        team_data["overall"]["losses"] += 1
                        team_data["seasons"][season]["losses"] += 1
                    
                    # MOM Filter: Check only the name used in this specific file
                    current_rcb_name = next(name for name in RCB_NAMES if name in teams)
                    rcb_roster = info.get('players', {}).get(current_rcb_name, [])
                    for p in info.get('player_of_match', []):
                        if p in rcb_roster:
                            team_data["overall"]["mom"][p] = team_data["overall"]["mom"].get(p, 0) + 1
                            team_data["seasons"][season]["mom"][p] = team_data["seasons"][season]["mom"].get(p, 0) + 1
            except Exception:
                continue
                
    with open(os.path.join(base_dir, "data", "team_stats_data.json"), 'w') as f:
        json.dump(team_data, f)
    print(f"Team indexing complete. Processed seasons: {sorted(team_data['seasons'].keys())}")

if __name__ == "__main__":
    run_team_indexer()