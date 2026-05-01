"""
Single match predictor: given two team names and match conditions,
predicts the winner using the trained ensemble model.
"""
import os
import sys
import argparse
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import PROCESSED_MATCHES_CSV
import src.prediction.predict_2026 as p26
from src.prediction.predict_2026 import build_matchup_features

def predict_match(team1: str, team2: str, venue: str = None,
                  toss_winner: str = None, toss_decision: str = None) -> dict:
    from src.models.ensemble_model import EnsembleModel

    try:
        model = EnsembleModel()
        model.load()
    except FileNotFoundError:
        from src.models.xgboost_model import XGBoostModel
        model = XGBoostModel()
        model.load()

    matches_df = pd.read_csv(PROCESSED_MATCHES_CSV)

    # HACK: If a specific venue is provided, force the feature builder to ONLY use that venue
    original_venues = p26.PREDICTION_VENUES
    if venue:
        p26.PREDICTION_VENUES = [venue]

    # Build features
    feats = build_matchup_features(team1, team2, matches_df)

    # Restore original venues so we don't break anything else
    p26.PREDICTION_VENUES = original_venues

    # Override toss if specified
    if toss_winner is not None:
        feats["toss_won_by_team1"] = int(toss_winner == team1)
    
    if toss_decision is not None:
        feats["toss_decision_bat"] = int(toss_decision == "bat")

    # Predict
    probs = model.predict_proba(feats)
    t1_prob = probs[:, 1].mean()
    t2_prob = 1 - t1_prob

    from config import TEAMS
    winner = team1 if t1_prob >= 0.5 else team2

    return {
        "team1": team1,
        "team1_name": TEAMS.get(team1, team1),
        "team1_win_prob": round(t1_prob * 100, 2),
        "team2": team2,
        "team2_name": TEAMS.get(team2, team2),
        "team2_win_prob": round(t2_prob * 100, 2),
        "predicted_winner": winner,
        "predicted_winner_name": TEAMS.get(winner, winner),
        "confidence": round(max(t1_prob, t2_prob) * 100, 2),
        "venue": venue if venue else "Averaged across venues",
        "toss_winner": toss_winner if toss_winner else "Averaged",
        "toss_decision": toss_decision if toss_decision else "Averaged"
    }

def print_match_result(result: dict):
    print("\n" + "─"*60)
    print(f"  MATCH PREDICTION (CUSTOM CONDITIONS)")
    print("─"*60)
    print(f"  Venue:         {result['venue']}")
    print(f"  Toss Winner:   {result['toss_winner']}")
    print(f"  Toss Decision: {result['toss_decision']}")
    print("─"*60)
    print(f"  {result['team1_name']:<30} {result['team1_win_prob']:>6.2f}%")
    print(f"  {result['team2_name']:<30} {result['team2_win_prob']:>6.2f}%")
    print("─"*60)
    print(f"  Winner: {result['predicted_winner_name']}  ({result['confidence']:.2f}% confidence)")
    print("─"*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict a specific IPL match with exact conditions.")
    parser.add_argument("team1", type=str, help="First team abbreviation (e.g., DC)")
    parser.add_argument("team2", type=str, help="Second team abbreviation (e.g., MI)")
    parser.add_argument("--venue", type=str, default=None, help="Exact venue name in quotes")
    parser.add_argument("--toss", type=str, default=None, help="Team abbreviation that won the toss")
    parser.add_argument("--decision", type=str, choices=["bat", "field"], default=None, help="Toss decision")

    args = parser.parse_args()
    result = predict_match(args.team1, args.team2, args.venue, args.toss, args.decision)
    print_match_result(result)