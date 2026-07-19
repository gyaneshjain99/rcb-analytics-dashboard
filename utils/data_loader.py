# utils/data_loader.py
import json

def load_team_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)