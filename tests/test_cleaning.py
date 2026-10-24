"""
IPL Analytics Pro - Data Cleaning and Integrity Tests
Tests data structures, boundary logic, extras summation, and season coverage.
"""

import os
import pytest
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

@pytest.fixture(scope="module")
def matches_and_deliveries():
    df_m = pd.read_csv(os.path.join(PROCESSED_DIR, "matches_cleaned.csv"))
    df_d = pd.read_parquet(os.path.join(PROCESSED_DIR, "deliveries_cleaned.parquet"))
    return df_m, df_d

def test_matches_structure(matches_and_deliveries):
    df_m, _ = matches_and_deliveries
    assert len(df_m) == 1243
    assert df_m["match_id"].nunique() == 1243
    assert df_m["season"].min() == 2008
    assert df_m["season"].max() == 2026
    
def test_deliveries_rules(matches_and_deliveries):
    _, df_d = matches_and_deliveries
    assert len(df_d) == 295732
    
    # Extras calculation
    calc_extras = df_d["wides"] + df_d["noballs"] + df_d["byes"] + df_d["legbyes"] + df_d["penalty"]
    assert (df_d["extras"] == calc_extras).all()
    
    # Total runs
    calc_total = df_d["runs_off_bat"] + df_d["extras"]
    assert (df_d["total_runs"] == calc_total).all()
    
    # Bowler runs conceded
    calc_bowler_runs = df_d["runs_off_bat"] + df_d["wides"] + df_d["noballs"]
    assert (df_d["bowler_runs_conceded"] == calc_bowler_runs).all()
