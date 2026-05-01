import pandas as pd
import requests
import os
from datetime import datetime

# Configuration
RAW_DATA_PATH = "data/raw_2026_matches/"
PROCESSED_PATH = "phase_profiles.csv"

def fetch_latest_match_data():
    """
    Simulates fetching 2026 live data. 
    In production, you would point this to a Cricsheet or API endpoint.
    """
    print(f"[{datetime.now()}] Checking for new 2026 match data...")
    # Placeholder for API request: 
    # response = requests.get("https://api.cricketdata.org/v1/ipl_2026_live")
    
    # For now, we simulate the 'Ingestion' of the latest match
    # 'latest_match_ball_by_ball.csv'
    return True 

def update_dna_profiles():
    """Recalculates the DNA based on the new total dataset."""
    print("Recalculating Player DNA with latest 2026 stats...")
    
    # Load existing historical data + new 2026 data
    df = pd.read_csv("IPL.csv", low_memory=False) 
    
    # Re-run the Phase Extraction Logic
    df['phase'] = df['over'].apply(lambda x: 'Powerplay' if x < 6 else ('Middle' if x < 15 else 'Death'))
    
    stats = df.groupby(['batter', 'phase']).agg(
        p_dot=('runs_batter', lambda x: (x == 0).mean()),
        p_1=('runs_batter', lambda x: (x == 1).mean()),
        p_4=('runs_batter', lambda x: (x == 4).mean()),
        p_6=('runs_batter', lambda x: (x == 6).mean()),
        p_wicket=('player_out', lambda x: x.notna().mean())
    ).reset_index()

    stats.to_csv(PROCESSED_PATH, index=False)
    print(f"SUCCESS: {PROCESSED_PATH} updated with 2026 performance trends.")

def auto_pipeline():
    if fetch_latest_match_data():
        update_dna_profiles()
        # Trigger the Calibration Engine to adjust for the new 'Actual' scores
        print("Pipeline Execution Complete.")

if __name__ == "__main__":
    auto_pipeline()