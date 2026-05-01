import pandas as pd

print("Analyzing Matchup DNA: Batter vs. Bowling Styles...")

# Using the historical base to build style-based probabilities
df = pd.read_csv("IPL.csv", low_memory=False)

# 1. Define Bowling Styles (Mapping common bowlers to styles)
# Note: In a full production 2026 model, you would join this with a player-style database.
style_map = {
    'Rashid Khan': 'Leg-break', 'YS Chahal': 'Leg-break', 'Kuldeep Yadav': 'Left-arm Wrist-spin',
    'JJ Bumrah': 'Right-arm Fast', 'Mohammed Shami': 'Right-arm Fast', 'TA Boult': 'Left-arm Fast',
    'RA Jadeja': 'Left-arm Orthodox', 'R Ashwin': 'Right-arm Off-break', 'SP Narine': 'Right-arm Off-break'
}

# We'll map the available styles in our dataset
df['bowling_style'] = df['bowler'].map(style_map).fillna('Other Pace/Spin')

# 2. Calculate Strike Rate and Wicket Prob per Style
matchup_stats = df.groupby(['batter', 'bowling_style']).agg(
    balls_faced=('match_id', 'count'),
    total_runs=('runs_batter', 'sum'),
    wickets=('player_out', lambda x: x.notna().sum())
).reset_index()

# Filter for relevance (min 30 balls against a style)
matchup_stats = matchup_stats[matchup_stats['balls_faced'] >= 30].copy()
matchup_stats['strike_rate'] = (matchup_stats['total_runs'] / matchup_stats['balls_faced']) * 100
matchup_stats['out_rate'] = (matchup_stats['wickets'] / matchup_stats['balls_faced']) * 100

matchup_stats.to_csv("matchup_dna.csv", index=False)
print("SUCCESS! matchup_dna.csv generated.")