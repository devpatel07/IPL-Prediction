import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Matchup Data
try:
    df = pd.read_csv("matchup_dna.csv")
    rosters = pd.read_csv("rosters_2026.csv")
except FileNotFoundError:
    print("Run matchup_dna.py first!")
    exit()

def plot_matchup_heatmap(team_name):
    # Get 2026 roster for the team
    team_players = rosters[rosters['Team'] == team_name]['Player'].unique()
    
    # Filter DNA for these specific players
    team_matchups = df[df['batter'].isin(team_players)]
    
    if team_matchups.empty:
        print(f"No matchup data found for {team_name} players.")
        return

    # 2. Pivot data for Heatmap (Batter vs Bowling Style)
    # We will visualize Strike Rate
    pivot_sr = team_matchups.pivot(index="batter", columns="bowling_style", values="strike_rate")
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_sr, annot=True, cmap="YlGnBu", fmt=".1f", linewidths=.5)
    
    plt.title(f"2026 Tactical Heat Map: {team_name} Strike Rate vs. Bowling Styles")
    plt.xlabel("Bowling Style")
    plt.ylabel("Batter")
    plt.show()

# --- EXECUTE ---
# Select a 2026 team to visualize
plot_matchup_heatmap("Delhi Capitals")