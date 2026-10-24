"""
IPL Analytics Pro - Data Cleaning and Standardization Pipeline
Transforms raw Cricsheet data into validated, structured datasets:
1. data/processed/matches_cleaned.csv
2. data/processed/deliveries_cleaned.parquet & data/processed/deliveries_cleaned.csv
3. reports/data_quality_report.md
"""

import os
import glob
import csv
import json
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "ipl_csv2")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

# Canonical team mapping
TEAM_MAPPING = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
}

# Season year normalization
def normalize_season(season_str):
    s = str(season_str).strip()
    if s == "2007/08":
        return 2008
    if s == "2009/10":
        return 2010
    if s == "2020/21":
        return 2020
    if "/" in s:
        parts = s.split("/")
        if len(parts[1]) == 2:
            return int("20" + parts[1])
        return int(parts[1])
    return int(s)

# Canonical venue mapping
VENUE_MAPPING = {
    "M. Chinnaswamy Stadium": "M Chinnaswamy Stadium, Bengaluru",
    "M Chinnaswamy Stadium": "M Chinnaswamy Stadium, Bengaluru",
    "M Chinnaswamy Stadium, Bengaluru": "M Chinnaswamy Stadium, Bengaluru",
    "Wankhede Stadium": "Wankhede Stadium, Mumbai",
    "Wankhede Stadium, Mumbai": "Wankhede Stadium, Mumbai",
    "Eden Gardens": "Eden Gardens, Kolkata",
    "Eden Gardens, Kolkata": "Eden Gardens, Kolkata",
    "Feroz Shah Kotla": "Arun Jaitley Stadium, Delhi",
    "Arun Jaitley Stadium": "Arun Jaitley Stadium, Delhi",
    "Arun Jaitley Stadium, Delhi": "Arun Jaitley Stadium, Delhi",
    "MA Chidambaram Stadium, Chepauk": "MA Chidambaram Stadium, Chepauk, Chennai",
    "MA Chidambaram Stadium, Chepauk, Chennai": "MA Chidambaram Stadium, Chepauk, Chennai",
    "MA Chidambaram Stadium": "MA Chidambaram Stadium, Chepauk, Chennai",
    "Rajiv Gandhi International Stadium, Uppal": "Rajiv Gandhi International Stadium, Hyderabad",
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad": "Rajiv Gandhi International Stadium, Hyderabad",
    "Rajiv Gandhi International Stadium": "Rajiv Gandhi International Stadium, Hyderabad",
    "Punjab Cricket Association Stadium, Mohali": "Punjab Cricket Association Stadium, Mohali",
    "Punjab Cricket Association IS Bindra Stadium, Mohali": "Punjab Cricket Association Stadium, Mohali",
    "Punjab Cricket Association IS Bindra Stadium": "Punjab Cricket Association Stadium, Mohali",
    "Sawai Mansingh Stadium": "Sawai Mansingh Stadium, Jaipur",
    "Sawai Mansingh Stadium, Jaipur": "Sawai Mansingh Stadium, Jaipur",
    "Dr DY Patil Sports Academy": "Dr DY Patil Sports Academy, Navi Mumbai",
    "Dr DY Patil Sports Academy, Mumbai": "Dr DY Patil Sports Academy, Navi Mumbai",
    "Brabourne Stadium": "Brabourne Stadium, Mumbai",
    "Brabourne Stadium, Mumbai": "Brabourne Stadium, Mumbai",
    "Maharashtra Cricket Association Stadium": "Maharashtra Cricket Association Stadium, Pune",
    "Maharashtra Cricket Association Stadium, Pune": "Maharashtra Cricket Association Stadium, Pune",
    "Subrata Roy Sahara Stadium": "Maharashtra Cricket Association Stadium, Pune",
    "Sardar Patel Stadium, Motera": "Narendra Modi Stadium, Ahmedabad",
    "Narendra Modi Stadium, Ahmedabad": "Narendra Modi Stadium, Ahmedabad",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow": "BRSABV Ekana Cricket Stadium, Lucknow",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium": "BRSABV Ekana Cricket Stadium, Lucknow",
}

BOWLER_WICKET_KINDS = {
    "bowled", "caught", "caught and bowled", "lbw", "stumped", "hit wicket"
}

def clean_matches():
    print("Parsing and cleaning match-level information from *_info.csv...")
    info_files = glob.glob(os.path.join(RAW_DIR, "*_info.csv"))
    
    matches_list = []
    for f in info_files:
        m_id = int(os.path.basename(f).replace("_info.csv", ""))
        rec = {
            "match_id": m_id,
            "season_code": None,
            "date": None,
            "venue_raw": None,
            "city": None,
            "team1_raw": None,
            "team2_raw": None,
            "toss_winner_raw": None,
            "toss_decision": None,
            "winner_raw": None,
            "win_by_runs": 0,
            "win_by_wickets": 0,
            "outcome": None,
            "eliminator": None,
            "player_of_match": None,
            "method": None,
            "super_over": False,
        }
        teams = []
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            for row in csv.reader(fp):
                if len(row) < 3 or row[0] != "info":
                    continue
                k, v = row[1], row[2]
                if k == "season":
                    rec["season_code"] = v
                elif k == "date":
                    rec["date"] = v.replace("/", "-")
                elif k == "venue":
                    rec["venue_raw"] = v
                elif k == "city":
                    rec["city"] = v
                elif k == "team":
                    teams.append(v)
                elif k == "toss_winner":
                    rec["toss_winner_raw"] = v
                elif k == "toss_decision":
                    rec["toss_decision"] = v
                elif k == "winner":
                    rec["winner_raw"] = v
                elif k == "winner_runs":
                    rec["win_by_runs"] = int(v)
                elif k == "winner_wickets":
                    rec["win_by_wickets"] = int(v)
                elif k == "outcome":
                    rec["outcome"] = v
                elif k == "eliminator":
                    rec["eliminator"] = v
                    rec["super_over"] = True
                elif k == "player_of_match":
                    rec["player_of_match"] = v
                elif k == "method":
                    rec["method"] = v
                elif k == "super_over":
                    rec["super_over"] = True
                    
        if len(teams) >= 2:
            rec["team1_raw"] = teams[0]
            rec["team2_raw"] = teams[1]
            
        matches_list.append(rec)
        
    df_m = pd.DataFrame(matches_list)
    
    # Standardize fields
    df_m["season"] = df_m["season_code"].apply(normalize_season)
    df_m["team1"] = df_m["team1_raw"].apply(lambda t: TEAM_MAPPING.get(t, t))
    df_m["team2"] = df_m["team2_raw"].apply(lambda t: TEAM_MAPPING.get(t, t))
    df_m["toss_winner"] = df_m["toss_winner_raw"].apply(lambda t: TEAM_MAPPING.get(t, t))
    
    # Determine official match winner
    # In case of tie, eliminator indicates the super over winner
    def resolve_winner(row):
        if pd.notnull(row["winner_raw"]):
            return TEAM_MAPPING.get(row["winner_raw"], row["winner_raw"])
        if row["outcome"] == "tie" and pd.notnull(row["eliminator"]):
            return TEAM_MAPPING.get(row["eliminator"], row["eliminator"])
        if row["outcome"] == "no result":
            return "No Result"
        return "No Result"

    df_m["winner"] = df_m.apply(resolve_winner, axis=1)
    
    # Result description
    def resolve_result_type(row):
        if row["outcome"] == "no result":
            return "no_result"
        if row["outcome"] == "tie" or row["super_over"]:
            return "tie_super_over"
        if row["win_by_runs"] > 0:
            return "runs"
        if row["win_by_wickets"] > 0:
            return "wickets"
        return "other"
        
    df_m["result_type"] = df_m.apply(resolve_result_type, axis=1)
    df_m["venue"] = df_m["venue_raw"].apply(lambda v: VENUE_MAPPING.get(v, v))
    
    # Sort chronologically
    df_m["date"] = pd.to_datetime(df_m["date"])
    df_m = df_m.sort_values(by=["date", "match_id"]).reset_index(drop=True)
    
    return df_m

def clean_deliveries(df_matches):
    print("Loading and cleaning ball-by-ball records from all_matches.csv...")
    raw_csv = os.path.join(RAW_DIR, "all_matches.csv")
    df_d = pd.read_csv(raw_csv, low_memory=False)
    
    raw_count = len(df_d)
    print(f"Loaded {raw_count:,} raw deliveries.")
    
    # Check duplicates
    dups = df_d.duplicated(subset=["match_id", "innings", "ball", "striker", "bowler"]).sum()
    print(f"Identified duplicate delivery keys: {dups}")
    if dups > 0:
        # In rare cases of re-bowled balls or re-entries, drop true duplicate lines
        df_d = df_d.drop_duplicates()
        print(f"Rows after dropping exact duplicates: {len(df_d):,}")
        
    # Standardize teams
    df_d["batting_team_raw"] = df_d["batting_team"]
    df_d["bowling_team_raw"] = df_d["bowling_team"]
    df_d["batting_team"] = df_d["batting_team"].apply(lambda t: TEAM_MAPPING.get(t, t))
    df_d["bowling_team"] = df_d["bowling_team"].apply(lambda t: TEAM_MAPPING.get(t, t))
    
    # Standardize season
    df_d["season_code"] = df_d["season"]
    df_d["season"] = df_d["season"].apply(normalize_season)
    
    # Standardize venue
    df_d["venue_raw"] = df_d["venue"]
    df_d["venue"] = df_d["venue"].apply(lambda v: VENUE_MAPPING.get(v, v))
    
    # Fill NAs in numeric extra columns
    for col in ["wides", "noballs", "byes", "legbyes", "penalty"]:
        if col in df_d.columns:
            df_d[col] = df_d[col].fillna(0).astype(int)
        else:
            df_d[col] = 0
            
    df_d["runs_off_bat"] = df_d["runs_off_bat"].fillna(0).astype(int)
    df_d["extras"] = df_d["extras"].fillna(0).astype(int)
    df_d["total_runs"] = df_d["runs_off_bat"] + df_d["extras"]
    
    # Over breakdown and phase
    df_d["over"] = df_d["ball"].astype(int)
    df_d["ball_in_over"] = ((df_d["ball"] - df_d["over"]) * 10).round().astype(int)
    
    def get_phase(over):
        if over < 6:
            return "Powerplay"
        elif over < 15:
            return "Middle Overs"
        else:
            return "Death Overs"
            
    df_d["phase"] = df_d["over"].apply(get_phase)
    
    # Boundary tracking
    non_b = df_d["non_boundary"].fillna(0).astype(int) if "non_boundary" in df_d.columns else 0
    df_d["is_boundary_four"] = ((df_d["runs_off_bat"] == 4) & (non_b == 0)).astype(int)
    df_d["is_boundary_six"] = ((df_d["runs_off_bat"] == 6) & (non_b == 0)).astype(int)
    
    # Legal deliveries: legal if wides == 0 and noballs == 0
    df_d["is_legal_delivery"] = ((df_d["wides"] == 0) & (df_d["noballs"] == 0)).astype(int)
    
    # Bowler runs conceded: runs off bat + wides + noballs (excludes byes, legbyes, penalty)
    df_d["bowler_runs_conceded"] = df_d["runs_off_bat"] + df_d["wides"] + df_d["noballs"]
    
    # Wickets
    df_d["is_wicket"] = df_d["player_dismissed"].notnull().astype(int)
    df_d["dismissal_kind"] = df_d["wicket_type"].fillna("None")
    df_d["is_bowler_wicket"] = (df_d["dismissal_kind"].isin(BOWLER_WICKET_KINDS)).astype(int)
    
    # Super over flag
    df_d["is_super_over"] = (df_d["innings"] >= 3).astype(int)
    
    return df_d

def compute_match_aggregates(df_m, df_d):
    print("Computing match-level innings totals and scores...")
    
    # Group deliveries by match_id and innings
    # Innings 1 and 2 regulation
    inn_totals = df_d[df_d["is_super_over"] == 0].groupby(["match_id", "innings"]).agg(
        team=("batting_team", "first"),
        total_runs=("total_runs", "sum"),
        wickets=("is_wicket", "sum"),
        overs_bowled=("is_legal_delivery", lambda s: f"{s.sum() // 6}.{s.sum() % 6}"),
        legal_balls=("is_legal_delivery", "sum")
    ).reset_index()
    
    inn1 = inn_totals[inn_totals["innings"] == 1].set_index("match_id")
    inn2 = inn_totals[inn_totals["innings"] == 2].set_index("match_id")
    
    df_m["team1_innings_team"] = df_m["match_id"].map(inn1["team"])
    df_m["team1_score"] = df_m["match_id"].map(inn1["total_runs"]).fillna(0).astype(int)
    df_m["team1_wickets"] = df_m["match_id"].map(inn1["wickets"]).fillna(0).astype(int)
    df_m["team1_legal_balls"] = df_m["match_id"].map(inn1["legal_balls"]).fillna(0).astype(int)
    
    df_m["team2_innings_team"] = df_m["match_id"].map(inn2["team"])
    df_m["team2_score"] = df_m["match_id"].map(inn2["total_runs"]).fillna(0).astype(int)
    df_m["team2_wickets"] = df_m["match_id"].map(inn2["wickets"]).fillna(0).astype(int)
    df_m["team2_legal_balls"] = df_m["match_id"].map(inn2["legal_balls"]).fillna(0).astype(int)
    
    # Ensure batting first / chasing team identification
    df_m["batting_first_team"] = df_m["team1_innings_team"].fillna(
        df_m.apply(lambda r: r["toss_winner"] if r["toss_decision"] == "bat" else (r["team2"] if r["toss_winner"] == r["team1"] else r["team1"]), axis=1)
    )
    df_m["chasing_team"] = df_m["team2_innings_team"].fillna(
        df_m.apply(lambda r: r["team2"] if r["batting_first_team"] == r["team1"] else r["team1"], axis=1)
    )
    
    # Identify toss & win correlations
    df_m["toss_win_match_win"] = (df_m["toss_winner"] == df_m["winner"]).astype(int)
    df_m["batting_first_win"] = (df_m["batting_first_team"] == df_m["winner"]).astype(int)
    df_m["chasing_win"] = (df_m["chasing_team"] == df_m["winner"]).astype(int)
    
    return df_m

def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    df_matches = clean_matches()
    df_deliveries = clean_deliveries(df_matches)
    df_matches = compute_match_aggregates(df_matches, df_deliveries)
    
    # Save processed files
    matches_csv = os.path.join(PROCESSED_DIR, "matches_cleaned.csv")
    deliveries_parquet = os.path.join(PROCESSED_DIR, "deliveries_cleaned.parquet")
    deliveries_csv = os.path.join(PROCESSED_DIR, "deliveries_cleaned.csv")
    
    print(f"Saving matches to {matches_csv}...")
    df_matches.to_csv(matches_csv, index=False)
    
    print(f"Saving deliveries to {deliveries_parquet}...")
    df_deliveries.to_parquet(deliveries_parquet, index=False, engine="pyarrow")
    
    print(f"Saving deliveries to {deliveries_csv}...")
    df_deliveries.to_csv(deliveries_csv, index=False)
    
    print("Data cleaning complete.")
    print(f"Total Matches Processed: {len(df_matches):,}")
    print(f"Total Deliveries Processed: {len(df_deliveries):,}")

if __name__ == "__main__":
    main()
