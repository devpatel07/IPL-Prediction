import pandas as pd

# Load the project data
try:
    phase_dna = pd.read_csv("phase_profiles.csv")
    rosters = pd.read_csv("rosters_2026.csv")
except FileNotFoundError:
    print("Error: Ensure you run phase_profiles.py and extract_rosters.py first!")
    exit()

def get_best_xi(team_name):
    # Filter only players in the official 2026 squad for this team
    team_squad = rosters[rosters['Team'] == team_name]['Player'].unique()
    team_dna = phase_dna[phase_dna['batter'].isin(team_squad)].copy()

    if team_dna.empty:
        return []

    # 1. OPENER FITNESS (Powerplay Focus)
    openers = team_dna[team_dna['phase'] == 'Powerplay'].copy()
    if not openers.empty:
        openers['fitness'] = (openers['p_4'] * 2) + (openers['p_6'] * 4) - (openers['p_wicket'] * 10)
        best_openers = openers.sort_values(by='fitness', ascending=False).head(2)['batter'].tolist()
    else:
        best_openers = []

    # 2. ANCHOR FITNESS (Middle Overs Focus)
    anchors = team_dna[team_dna['phase'] == 'Middle'].copy()
    if not anchors.empty:
        # We use fillna(0) just in case some columns are empty
        anchors['fitness'] = (anchors['p_1'] + (anchors['p_2'] * 2)) - (anchors['p_wicket'] * 15)
        best_anchors = anchors[~anchors['batter'].isin(best_openers)].sort_values(by='fitness', ascending=False).head(4)['batter'].tolist()
    else:
        best_anchors = []

    # 3. FINISHER FITNESS (Death Overs Focus)
    finishers = team_dna[team_dna['phase'] == 'Death'].copy()
    if not finishers.empty:
        finishers['fitness'] = (finishers['p_6'] * 6) + (finishers['p_4'] * 3) - (finishers['p_dot'] * 5)
        best_finishers = finishers[~finishers['batter'].isin(best_openers + best_anchors)].sort_values(by='fitness', ascending=False).head(5)['batter'].tolist()
    else:
        best_finishers = []

    return best_openers + best_anchors + best_finishers

# --- EXECUTE ---
test_team = "Delhi Capitals" # Or "Rajasthan Royals"
recommended_xi = get_best_xi(test_team)

if not recommended_xi:
    print(f"No data found for {test_team} in 2026.")
else:
    print(f"\n--- AI CAPTAIN: OPTIMAL 2026 XI FOR {test_team.upper()} ---")
    for i, player in enumerate(recommended_xi, 1):
        role = "Opener" if i <= 2 else ("Anchor" if i <= 6 else "Finisher/Lower Order")
        print(f"Slot {i}: {player:<25} | Role: {role}")