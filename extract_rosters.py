import pandas as pd

print("Scanning ONLY 2026 match data to extract CURRENT rosters...")

try:
    df = pd.read_csv("cricsheet.csv", low_memory=False)
    
    # Convert 'start_date' to datetime so we can filter by year
    df['start_date'] = pd.to_datetime(df['start_date'])
    
    # FILTER: Only keep players who have actually stepped on the field in 2026
    df_2026 = df[df['start_date'].dt.year == 2026].copy()

    if df_2026.empty:
        print("Warning: No matches found for the year 2026 in cricsheet.csv!")
        exit()

    # Extract batters and bowlers for 2026
    batters = df_2026[['batting_team', 'striker']].rename(columns={'batting_team': 'Team', 'striker': 'Player'})
    bowlers = df_2026[['bowling_team', 'bowler']].rename(columns={'bowling_team': 'Team', 'bowler': 'Player'})

    # Combine and clean
    current_rosters = pd.concat([batters, bowlers]).drop_duplicates().dropna()
    current_rosters = current_rosters.sort_values(by=['Team', 'Player'])

    current_rosters.to_csv("rosters_2026.csv", index=False)
    
    print(f"\nSUCCESS! Found {len(current_rosters)} active players for the 2026 season.")
    
    # Verify DC Count
    dc_count = len(current_rosters[current_rosters['Team'] == 'Delhi Capitals'])
    print(f"Current Delhi Capitals 2026 Squad Size: {dc_count}")

except Exception as e:
    print(f"Error: {e}")