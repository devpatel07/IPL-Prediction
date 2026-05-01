import pandas as pd
import json
import os

# 1. Load Actual 2026 Data (Ensure your CSV is updated with today's match)
def run_self_correction(match_id, actual_total, predicted_total, venue_name):
    print(f"--- CALIBRATING ENGINE FOR MATCH {match_id} ---")
    
    # Calculate the error percentage
    error_margin = (actual_total - predicted_total) / predicted_total
    
    # Load existing calibration data
    if os.path.exists("calibration_factors.json"):
        with open("calibration_factors.json", "r") as f:
            cal_data = json.load(f)
    else:
        cal_data = {"venue_adjustments": {}}

    # 2. Adjust Venue Multiplier
    # If the actual score was 20% higher than predicted, we boost the venue multiplier
    current_adj = cal_data["venue_adjustments"].get(venue_name, 1.0)
    new_adj = current_adj * (1 + (error_margin * 0.5)) # 0.5 is the 'Learning Rate'
    
    cal_data["venue_adjustments"][venue_name] = round(new_adj, 3)
    cal_data["last_updated"] = "2026-05-01"

    with open("calibration_factors.json", "w") as f:
        json.dump(cal_data, f, indent=4)
        
    print(f"Correction applied for {venue_name}. New Calibration Factor: {new_adj}")

# --- TEST SCENARIO ---
# Let's say your simulation predicted 160 for DC, but they actually scored 190 at Arun Jaitley Stadium.
run_self_correction(match_id="IPL2026_M35", actual_total=190, predicted_total=160, venue_name="Arun Jaitley Stadium")