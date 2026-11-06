"""
RR TalentIQ - Unit Tests for Bowling Scouting Engine & Dual Discipline Engine
Validates bowling impact index, decimal overs, all-rounder balance penalties,
and wicketkeeper composite indexing.
"""

import pytest
import pandas as pd
from analytics.bowling_scouting import BowlingScoutingEngine
from analytics.allrounder_scouting import DualDisciplineScoutingEngine


@pytest.fixture
def bowling_engine():
    return BowlingScoutingEngine(min_overs_threshold=10.0)


@pytest.fixture
def dual_engine():
    return DualDisciplineScoutingEngine()


def test_bowling_metrics_calculation(bowling_engine):
    """Verifies bowling impact calculation, decimal overs, and dot ball estimation."""
    df = pd.DataFrame([{
        "player_name": "Strike Pacer",
        "bowling_style": "Right-arm fast",
        "matches": 15,
        "innings_bowled": 15,
        "overs": 54.4,  # 54 overs and 4 balls = 54.67 decimal overs
        "balls_bowled": 328,
        "wickets": 26,
        "runs_conceded": 390,
        "economy": 7.13,
        "bowling_average": 15.0,
        "bowling_strike_rate": 12.62,
        "dot_ball_pct_bowl": 48.0
    }])

    enriched = bowling_engine.calculate_bowling_metrics(df)
    row = enriched.iloc[0]

    assert row["decimal_overs"] == 54.67
    assert row["wickets_per_innings"] == round(26 / 15, 2)
    assert row["estimated_dot_balls"] > 140
    assert row["bowling_impact_index"] > 60.0
    assert row["sample_confidence_bowl"] > 0.85


def test_allrounder_balance_penalizes_one_way_player(dual_engine):
    """
    Ensures that a pure batter who bowled 2 fluke overs does not receive
    a high All-Rounder Composite Score, enforcing harmonic mean gating.
    """
    df = pd.DataFrame([
        {
            "player_name": "Genuine All-Rounder",
            "matches": 20,
            "innings_batted": 18,
            "runs": 450,
            "balls_faced": 300,
            "strike_rate": 150.0,
            "batting_average": 37.5,
            "fours": 40,
            "sixes": 20,
            "dot_ball_pct_bat": 30.0,
            "boundary_pct_bat": 62.2,
            "innings_bowled": 18,
            "overs": 60.0,
            "balls_bowled": 360,
            "wickets": 22,
            "runs_conceded": 450,
            "economy": 7.50,
            "bowling_average": 20.45,
            "bowling_strike_rate": 16.36,
            "dot_ball_pct_bowl": 45.0,
            "catches": 8,
            "stumpings": 0
        },
        {
            "player_name": "Pure Batter Part-Timer",
            "matches": 20,
            "innings_batted": 20,
            "runs": 650,
            "balls_faced": 400,
            "strike_rate": 162.5,
            "batting_average": 45.0,
            "fours": 65,
            "sixes": 30,
            "dot_ball_pct_bat": 28.0,
            "boundary_pct_bat": 66.0,
            "innings_bowled": 2,
            "overs": 2.0,  # Below minimum 10 overs threshold
            "balls_bowled": 12,
            "wickets": 2,
            "runs_conceded": 14,
            "economy": 7.00,
            "bowling_average": 7.00,
            "bowling_strike_rate": 6.00,
            "dot_ball_pct_bowl": 50.0,
            "catches": 6,
            "stumpings": 0
        }
    ])

    evaluated = dual_engine.evaluate_allrounders(df)
    gen_ar = evaluated[evaluated["player_name"] == "Genuine All-Rounder"].iloc[0]
    part_timer = evaluated[evaluated["player_name"] == "Pure Batter Part-Timer"].iloc[0]

    assert gen_ar["allrounder_composite_score"] > 40.0
    # Part timer should be severely penalized on composite allrounder score
    assert part_timer["allrounder_composite_score"] < 25.0
    assert "Genuine" in gen_ar["allrounder_archetype"]


def test_wicketkeeper_composite_evaluation(dual_engine):
    """Verifies that wicketkeeper composite score properly blends batting and keeping indices."""
    df = pd.DataFrame([{
        "player_name": "Talented Keeper",
        "matches": 16,
        "innings_batted": 15,
        "runs": 480,
        "balls_faced": 320,
        "strike_rate": 150.0,
        "batting_average": 40.0,
        "fours": 45,
        "sixes": 18,
        "dot_ball_pct_bat": 32.0,
        "boundary_pct_bat": 60.0,
        "catches": 18,
        "stumpings": 6
    }])

    wk_df = dual_engine.evaluate_wicketkeepers(df)
    row = wk_df.iloc[0]

    assert row["total_dismissals"] == 24
    assert row["dismissals_per_match"] == 1.5
    assert row["stumping_ratio"] == 0.25  # 6 / 24
    assert row["keeping_impact_index"] > 60.0
    assert row["wicketkeeper_composite_score"] > 50.0

