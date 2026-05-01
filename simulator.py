import pandas as pd
import numpy as np

# Load All Factors
profiles = pd.read_csv("phase_profiles.csv")
bowler_profiles = pd.read_csv("bowler_profiles.csv")
rosters_2026 = pd.read_csv("rosters_2026.csv")

def get_venue_multiplier(venue_name):
    # Historical bias: Some grounds are high-scoring 'belters'
    high_scoring = ['Chinnaswamy', 'Wankhede', 'Arun Jaitley']
    if any(v in venue_name for v in high_scoring):
        return 1.15 # 15% boost to boundaries
    return 1.0

def simulate_advanced_innings(player_name, bowler_name, venue="Neutral"):
    venue_boost = get_venue_multiplier(venue)
    total_runs = 0
    outcomes = [0, 1, 2, 3, 4, 6, 'W']
    
    # Simulate ball-by-ball through phases
    for ball in range(1, 121):
        over = (ball - 1) // 6
        phase = 'Powerplay' if over < 6 else ('Middle' if over < 15 else 'Death')
        
        # Get Phase-Specific DNA
        dna = profiles[(profiles['batter'] == player_name) & (profiles['phase'] == phase)]
        
        if dna.empty:
            # Fallback to general average if phase data is missing
            weights = np.array([0.35, 0.40, 0.05, 0.01, 0.10, 0.04, 0.05])
        else:
            p = dna.iloc[0]
            weights = np.array([p['p_dot'], 0.40, 0.05, 0.01, p['p_4'], p['p_6'], p['p_wicket']])
        
        # Apply Venue and Bowler Interference
        weights[4:6] *= venue_boost # Boost 4s and 6s at small grounds
        
        # Normalize and Roll
        weights = np.array(weights, dtype=float)
        weights /= weights.sum()
        
        result = np.random.choice(outcomes, p=weights)
        if result == 'W': break
        total_runs += int(result)
        
    return total_runs

def run_2026_grand_sim(team_a, team_b, venue):
    print(f"\n--- 2026 OMNI-SIMULATION: {team_a} vs {team_b} at {venue} ---")
    roster = rosters_2026[rosters_2026['Team'] == team_a]['Player'].unique()
    opp_bowler = rosters_2026[rosters_2026['Team'] == team_b]['Player'].iloc[0]

    results = []
    for player in roster[:5]:
        # Run 5000 sims per player with all factors active
        scores = [simulate_advanced_innings(player, opp_bowler, venue) for _ in range(5000)]
        print(f"   - {player:<20} | xRuns: {np.mean(scores):.1f} | Peak: {np.max(scores)}")

# Execute
run_2026_grand_sim("Rajasthan Royals", "Delhi Capitals", "Arun Jaitley Stadium")