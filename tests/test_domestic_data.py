"""
RR TalentIQ - Unit Tests for Domestic Data Ingestion & Quality Engine
Validates adaptive loading, schema mapping, statistics validation, and data quality audits.
"""

import os
import pytest
import pandas as pd
import numpy as np
from analytics.domestic_data_loader import DomesticDataLoader, STANDARDIZED_COLUMNS

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CSV = os.path.join(PROJECT_ROOT, "data", "sample", "domestic_players_sample.csv")

@pytest.fixture
def loader():
    return DomesticDataLoader()

def test_loader_standardized_schema(loader):
    """Verifies that unified scouting data conforms strictly to the canonical 36-column schema."""
    df = loader.load_unified_scouting_data(include_synthetic=False)
    assert len(df) >= 15
    for col in STANDARDIZED_COLUMNS:
        assert col in df.columns, f"Missing required column: {col}"
    assert "is_synthetic" in df.columns
    assert (df["is_synthetic"] == False).all()

def test_adaptive_column_synonyms(loader):
    """Tests that disparate column name formats (e.g. 'bf', 'rc', 'ov', 'mat') are correctly mapped."""
    messy_data = pd.DataFrame([{
        "name": "Arjun Test",
        "birth_date": "2004-05-10",
        "category": "Pace Bowler",
        "mat": 8,
        "runs_scored": 45,
        "bf": 30,
        "ov": 28.0,
        "rc": 196,
        "wkts": 14,
        "is_uncapped": "Confirmed Uncapped"
    }])
    standardized = loader.standardize_player_dataset(messy_data, data_source="Messy Schema Test")
    
    assert standardized.iloc[0]["player_name"] == "Arjun Test"
    assert standardized.iloc[0]["playing_role"] == "Pace Bowler"
    assert standardized.iloc[0]["matches"] == 8
    assert standardized.iloc[0]["runs"] == 45
    assert standardized.iloc[0]["balls_faced"] == 30
    assert standardized.iloc[0]["wickets"] == 14
    assert standardized.iloc[0]["runs_conceded"] == 196
    assert standardized.iloc[0]["economy"] == 7.0  # 196 / 28.0
    assert standardized.iloc[0]["strike_rate"] == 150.0  # (45 / 30) * 100

def test_age_calculation_from_dob(loader):
    """Verifies age is computed correctly from date of birth using the reference date."""
    dob_data = pd.DataFrame([{
        "player_name": "Young Prospect",
        "dob": "2005-01-01"
    }])
    standardized = loader.standardize_player_dataset(
        dob_data, 
        age_reference_date="2027-01-01"
    )
    # Exactly 22 years from 2005-01-01 to 2027-01-01
    assert standardized.iloc[0]["age"] == 22.0

def test_missing_dob_handling(loader):
    """Verifies that missing date of birth does not crash the loader and is cleanly flagged."""
    missing_data = pd.DataFrame([{
        "player_name": "Unknown Age Player",
        "dob": None
    }])
    standardized = loader.standardize_player_dataset(missing_data)
    assert standardized.iloc[0]["dob"] == "Unknown"
    assert np.isnan(standardized.iloc[0]["age"])

def test_cricket_stats_reconciliation(loader):
    """Tests proper arithmetic calculation for strike rate, boundary %, and economy."""
    stats_data = pd.DataFrame([{
        "player_name": "Power Hitter",
        "runs": 100,
        "balls_faced": 50,
        "fours": 10,
        "sixes": 5,
        "overs": 4.0,
        "runs_conceded": 32,
        "wickets": 2
    }])
    df = loader.standardize_player_dataset(stats_data)
    row = df.iloc[0]
    
    # SR = (100 / 50) * 100 = 200.0
    assert row["strike_rate"] == 200.0
    # Boundary runs = 10*4 + 5*6 = 70. Boundary % = 70 / 100 = 70.0%
    assert row["boundary_pct_bat"] == 70.0
    # Economy = 32 / 4.0 = 8.0
    assert row["economy"] == 8.0
    # Bowling SR = 24 balls / 2 wickets = 12.0
    assert row["bowling_strike_rate"] == 12.0

def test_data_quality_report_metrics(loader):
    """Verifies that the automated 10-point data quality report produces valid audit figures."""
    df = loader.load_unified_scouting_data(include_synthetic=True)
    report = loader.generate_data_quality_report(df)
    
    assert report["total_records"] >= 15
    assert report["duplicate_ids"] == 0
    assert "role_distribution" in report
    assert "uncapped_distribution" in report
    assert report["synthetic_records"] > 0  # Since include_synthetic=True
    assert report["audit_grade"] in ["A+", "A", "B"]

def test_synthetic_fixtures_never_in_authentic_data(loader):
    """Ensures synthetic fixtures are never blended into production data by default."""
    prod_df = loader.load_unified_scouting_data(include_synthetic=False)
    assert prod_df["is_synthetic"].sum() == 0
    assert not any(prod_df["player_name"].str.startswith("[SYNTHETIC-QA]"))

