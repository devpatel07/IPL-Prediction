import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="IPL 2026: Ultra-Turbo Engine", layout="wide")
st.title("🚀 IPL 2026: Ultra-Turbo Prediction Engine")

# --- 2. DATA LOADING (CACHED) ---
@st.cache_data
def load_core_data():
    try:
        dna = pd.read_csv("phase_profiles.csv")
        bwl = pd.read_csv("bowler_profiles.csv")
        ros = pd.read_csv("rosters_2026.csv")
        return dna, bwl, ros
    except: return None, None, None

phase_dna, bowler_dna, rosters = load_core_data()

# --- 3. EXHAUSTIVE STADIUM DATABASE ---
venues_db = {
    "High Scoring (Belters)": [
        "M. Chinnaswamy Stadium (Bengaluru)", "Wankhede Stadium (Mumbai)", 
        "Arun Jaitley Stadium (Delhi)", "Eden Gardens (Kolkata)", 
        "Brabourne Stadium (Mumbai)", "Holkar Cricket Stadium (Indore)", 
        "Sharjah Cricket Stadium (UAE)"
    ],
    "Balanced (Competitive)": [
        "Narendra Modi Stadium (Ahmedabad)", "Rajiv Gandhi International Stadium (Hyderabad)", 
        "IS Bindra Stadium (Mohali/Mullanpur)", "DY Patil Stadium (Navi Mumbai)", 
        "Dr. Y.S. Rajasekhara Reddy Stadium (Vizag)", "Barsapara Cricket Stadium (Guwahati)", 
        "Greenfield International Stadium (Thiruvananthapuram)", "Dubai International Cricket Stadium (UAE)"
    ],
    "Low Scoring (Bowler Friendly)": [
        "MA Chidambaram Stadium (Chepauk, Chennai)", "Ekana Cricket Stadium (Lucknow)", 
        "Sawai Mansingh Stadium (Jaipur)", "HPCA Stadium (Dharamshala)", 
        "JSCA International Stadium Complex (Ranchi)", "Saurashtra Cricket Association Stadium (Rajkot)", 
        "Zayed Cricket Stadium (Abu Dhabi)"
    ]
}

# --- 4. HELPER FUNCTIONS ---
def get_impact_stats(over, attack, b_lookup, impact_name, is_active):
    """Handles the mid-match substitution logic for 2026 rules."""
    if is_active and over >= 15:
        data = b_lookup.get(impact_name, {'economy_factor': 1.0, 'wicket_factor': 1.0})
        return {'eco': data['economy_factor'], 'wix': data['wicket_factor']}
    
    if over < 6: b_name = attack[0]
    elif over < 15: b_name = attack[1] if len(attack) > 1 else attack[0]
    else: b_name = attack[-1]
    
    data = b_lookup.get(b_name, {'economy_factor': 1.0, 'wicket_factor': 1.0})
    return {'eco': data['economy_factor'], 'wix': data['wicket_factor']}

# --- 5. HIGH-SPEED ENGINE ---
def run_ultra_innings(p_dna_map, attack_names, b_lookup, v_mult, start_over, wix_down, target, current, impact_name, use_impact):
    total = 0
    rem_overs = 20 - start_over
    outcomes = [0, 1, 2, 3, 4, 6, 7] # 7 = Wicket
    
    for o_idx in range(rem_overs):
        curr_over = start_over + o_idx
        bwl = get_impact_stats(curr_over, attack_names, b_lookup, impact_name, use_impact)
        
        for ball in range(6):
            phase = 'Powerplay' if curr_over < 6 else ('Middle' if curr_over < 15 else 'Death')
            w = p_dna_map.get(phase, np.array([0.35, 0.40, 0.05, 0.01, 0.08, 0.06, 0.05])).copy()

            if target > 0:
                b_left = ((rem_overs - o_idx) * 6) - ball
                rrr = ((target - (current + total)) / b_left) * 6 if b_left > 0 else 0
                if rrr > 12: w[5] *= 1.4; w[6] *= 1.5
            
            if wix_down > 6: w[0] *= 1.25
            
            w[4:6] *= v_mult
            w[4:6] /= bwl['eco']
            w[6] *= bwl['wix']

            w /= w.sum()
            res = np.random.choice(outcomes, p=w)
            if res == 7:
                wix_down += 1
                if wix_down >= 10: return total
            else: total += res
    return total

# --- 6. DEFINE TABS (CRITICAL ORDER) ---
tab_setup, tab_engine, tab_risk = st.tabs(["📋 Squad Setup", "⚡ Match Engine", "📊 Volatility Analysis"])

# --- TAB 1: SETUP ---
with tab_setup:
    col_v, col_s = st.columns(2)
    with col_v:
        st.subheader("Venue Selection")
        all_options = [f"{cat}: {g}" for cat, grounds in venues_db.items() for g in grounds]
        selected_v = st.selectbox("Select Stadium:", all_options)
        
        v_name = selected_v.split(": ")[1]
        b_mult = 1.18 if "High" in selected_v else (0.88 if "Low" in selected_v else 1.0)
        
        team_bat = st.selectbox("Batting Side:", sorted(rosters['Team'].unique()))
        team_bowl = st.selectbox("Bowling Side:", sorted(rosters['Team'].unique()), index=1)

    with col_s:
        st.subheader("Lineup Strategy")
        if st.button("🤖 AI Captain: Draft Best XI"):
            squad = rosters[rosters['Team'] == team_bat]['Player'].unique()
            st.session_state.best_bat = phase_dna[phase_dna['batter'].isin(squad)].groupby('batter')['p_6'].mean().nlargest(11).index.tolist()
        
        sel_batters = st.multiselect("Selected Lineup:", rosters[rosters['Team'] == team_bat]['Player'].unique(), 
                                      default=st.session_state.get('best_bat', []))
        sel_attack = st.multiselect("Main Attack (Min 3):", rosters[rosters['Team'] == team_bowl]['Player'].unique())

# --- TAB 2: ENGINE ---
with tab_engine:
    c1, c2, c3, c4 = st.columns(4)
    target = c1.number_input("Target", value=0)
    curr_score = c2.number_input("Score", value=0)
    live_over = c3.slider("Over", 0, 19, 0)
    live_wix = c4.slider("Wickets", 0, 9, 0)

    st.markdown("---")
    st.subheader("🔄 Impact Player Strategy")
    use_impact = st.toggle("Activate Impact Sub at Death (Over 16)")
    # Get team_bowl dynamically
    bowl_team_squad = rosters[rosters['Team'] == team_bowl]['Player'].unique()
    impact_name = st.selectbox("Select Impact Bowler:", bowl_team_squad)

    if st.button("🔥 RUN FULL MATCH SIMULATION"):
        if not sel_batters or len(sel_attack) < 2:
            st.error("Setup your lineup and attack in the 'Squad Setup' tab first.")
        else:
            bwl_lookup = bowler_dna.set_index('bowler').to_dict('index')
            p_data = phase_dna[phase_dna['batter'] == sel_batters[0]]
            p_dna_map = {row['phase']: np.array([row['p_dot'], row['p_1'], row['p_2'], row['p_3'], row['p_4'], row['p_6'], row['p_wicket']]) for _, row in p_data.iterrows()}

            with st.spinner("Crunching 1,000 parallel scenarios..."):
                sim_results = [run_ultra_innings(p_dna_map, sel_attack, bwl_lookup, b_mult, live_over, live_wix, target, curr_score, impact_name, use_impact) for _ in range(1000)]
            
            st.session_state.sim_data = sim_results
            st.metric("Expected Total", f"{int(curr_score + np.mean(sim_results))}")
            st.success("Analysis Complete!")
            st.line_chart(sim_results)

# --- TAB 3: RISK ---
with tab_risk:
    if 'sim_data' in st.session_state:
        st.subheader("Match Volatility Analysis")
        fig, ax = plt.subplots(figsize=(10, 4))
        plt.hist(st.session_state.sim_data, bins=30, color='#1f77b4', edgecolor='white')
        ax.set_title(f"Score Probability Distribution: {v_name}")
        ax.set_xlabel("Additional Runs Predicted")
        st.pyplot(fig)
    else:
        st.info("Run a simulation in the 'Match Engine' tab to generate volatility data.")