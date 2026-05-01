import pandas as pd
import requests
import io

def fetch_and_merge_2026():
    # URL for the 2026 match center JSON/CSV
    # In 2026, we typically use the Cricsheet or official IPL API endpoints
    url = "https://api.example.com/ipl-2026/latest-matches" 
    
    print("Fetching latest 2026 match results...")
    try:
        response = requests.get(url)
        new_data = pd.read_json(io.StringIO(response.text))
        
        # Load your LFS-tracked master file
        master_df = pd.read_csv("IPL.csv")
        
        # Append only new matches that aren't already in the master file
        updated_df = pd.concat([master_df, new_data]).drop_duplicates(subset=['match_id', 'ball'])
        
        # Save back to disk - Git LFS will handle the versioning
        updated_df.to_csv("IPL.csv", index=False)
        print("Master IPL.csv updated with latest 2026 matches.")
        return True
    except Exception as e:
        print(f"Update failed: {e}")
        return False

if __name__ == "__main__":
    fetch_and_merge_2026()
