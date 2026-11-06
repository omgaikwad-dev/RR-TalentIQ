"""
RR TalentIQ - Unit Tests for Batting Scouting Engine
Validates batting impact index, boundary percentage, non-boundary strike rotation,
and sample size confidence scaling.
"""

import pytest
import pandas as pd
from analytics.batting_scouting import BattingScoutingEngine


@pytest.fixture
def batting_engine():
    return BattingScoutingEngine(min_balls_threshold=30)


def test_batting_metrics_calculation(batting_engine):
    """Verifies calculated batting metrics on a controlled sample."""
    sample_df = pd.DataFrame([{
        "player_name": "Dynamic Finisher",
        "playing_role": "Finisher",
        "matches": 15,
        "innings_batted": 14,
        "runs": 450,
        "balls_faced": 250,
        "strike_rate": 180.0,
        "batting_average": 45.0,
        "fours": 35,
        "sixes": 25,
        "dot_ball_pct_bat": 28.0,
        "boundary_pct_bat": 64.44
    }])

    enriched = batting_engine.calculate_batting_metrics(sample_df)
    row = enriched.iloc[0]

    # Runs per innings
    assert row["runs_per_innings"] == round(450 / 14, 2)
    # Four % and Six %
    assert row["four_pct"] == round((35 / 250) * 100, 2)
    assert row["six_pct"] == round((25 / 250) * 100, 2)
    # Rotation strike rate
    assert row["rotation_strike_rate"] > 0
    # Batting impact index should be positive and high for 180 SR, 45 Avg
    assert row["batting_impact_index"] > 60.0
    # Sample confidence should be high for 250 balls
    assert row["sample_confidence_bat"] > 0.75


def test_sample_confidence_penalizes_tiny_sample(batting_engine):
    """Ensures a player with 1 fluke innings of 40 runs off 15 balls doesn't top the ranking."""
    df = pd.DataFrame([
        {
            "player_name": "Small Sample Fluke",
            "playing_role": "Finisher",
            "matches": 1,
            "innings_batted": 1,
            "runs": 40,
            "balls_faced": 15,
            "strike_rate": 266.67,
            "batting_average": 40.0,
            "fours": 4,
            "sixes": 3,
            "dot_ball_pct_bat": 20.0,
            "boundary_pct_bat": 85.0
        },
        {
            "player_name": "Proven Consistent Batter",
            "playing_role": "Finisher",
            "matches": 25,
            "innings_batted": 22,
            "runs": 650,
            "balls_faced": 400,
            "strike_rate": 162.5,
            "batting_average": 40.62,
            "fours": 60,
            "sixes": 30,
            "dot_ball_pct_bat": 27.0,
            "boundary_pct_bat": 64.6
        }
    ])

    enriched = batting_engine.calculate_batting_metrics(df)
    fluke = enriched[enriched["player_name"] == "Small Sample Fluke"].iloc[0]
    proven = enriched[enriched["player_name"] == "Proven Consistent Batter"].iloc[0]

    assert fluke["sample_confidence_bat"] < 0.20
    assert proven["sample_confidence_bat"] > 0.90
    # Proven batter MUST score higher on Batting Impact Index than fluke batter
    assert proven["batting_impact_index"] > fluke["batting_impact_index"]

