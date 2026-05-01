import pandas as pd

print("Extracting Bowler DNA from IPL.csv...")
df = pd.read_csv("IPL.csv", low_memory=False)

# Filter for valid deliveries (excluding wides)
valid_balls = df[df['balls_faced'] == 1].copy()

# Calculate Bowler Stats
bowler_stats = valid_balls.groupby('bowler').agg(
    balls_bowled=('match_id', 'count'),
    runs_conceded=('runs_batter', 'sum'),
    wickets_taken=('player_out', 'count')
).reset_index()

# Filter for experienced bowlers (min 60 balls/10 overs)
bowler_stats = bowler_stats[bowler_stats['balls_bowled'] >= 60].copy()

# Calculate Bowler weights (Economy and Strike Rate)
bowler_stats['economy_factor'] = (bowler_stats['runs_conceded'] / bowler_stats['balls_bowled']) / 1.5 # Normalized
bowler_stats['wicket_factor'] = (bowler_stats['wickets_taken'] / bowler_stats['balls_bowled']) * 10 # Normalized

bowler_stats.to_csv("bowler_profiles.csv", index=False)
print("SUCCESS! bowler_profiles.csv generated.")