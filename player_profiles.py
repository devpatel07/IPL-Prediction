import pandas as pd

print("Updating Phase-Specific DNA with full scoring matrix...")
# Ensure you are using the correct source file (IPL.csv or cricsheet.csv)
df = pd.read_csv("IPL.csv", low_memory=False)

def get_phase(over):
    if over < 6: return 'Powerplay'
    if over < 15: return 'Middle'
    return 'Death'

df['phase'] = df['over'].apply(get_phase)
valid_balls = df[df['balls_faced'] == 1].copy()

# Full aggregation including 1s, 2s, and 3s
phase_stats = valid_balls.groupby(['batter', 'phase']).agg(
    balls_faced=('match_id', 'count'),
    p_dot=('runs_batter', lambda x: (x == 0).mean()),
    p_1=('runs_batter', lambda x: (x == 1).mean()),
    p_2=('runs_batter', lambda x: (x == 2).mean()),
    p_3=('runs_batter', lambda x: (x == 3).mean()),
    p_4=('runs_batter', lambda x: (x == 4).mean()),
    p_6=('runs_batter', lambda x: (x == 6).mean()),
    p_wicket=('player_out', lambda x: x.notna().mean())
).reset_index()

# Filter for players with at least 20 balls in a phase for reliability
phase_stats = phase_stats[phase_stats['balls_faced'] >= 20]
phase_stats.to_csv("phase_profiles.csv", index=False)
print("SUCCESS! phase_profiles.csv now contains the full probability matrix.")