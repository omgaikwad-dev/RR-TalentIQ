"""
RR TalentIQ - Unit Tests for Player Ranking & Top 10 Recommendation Engine
Validates multi-criteria scoring, role classification, potential calculations,
sensitivity analysis, and SupeRR Selector Top 10 recommendations.
"""

import pytest
import pandas as pd
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.role_classifier import RoleClassifier, ROLE_WICKETKEEPER, ROLE_PACE_BOWLER
from scouting.potential_score import PotentialScoreEngine
from scouting.player_ranker import PlayerRanker
from scouting.recommendations import RecommendationEngine


@pytest.fixture
def loader():
    return DomesticDataLoader()


@pytest.fixture
def benchmark_data(loader):
    return loader.get_benchmarked_uncapped_talents()


def test_role_classifier_inference():
    """Verifies that player roles are inferred accurately based on stats."""
    # Player with stumpings should be classified as Wicketkeeper-Batter
    row_keeper = {"playing_role": "Batter", "stumpings": 5, "catches": 15, "runs": 300, "balls_faced": 200, "overs": 0}
    assert RoleClassifier.infer_role(row_keeper) == ROLE_WICKETKEEPER

    # Player with overs and fast bowling style should be Pace Bowler
    row_pacer = {"playing_role": "Bowler", "overs": 30.0, "balls_faced": 10, "bowling_style": "Right-arm fast", "stumpings": 0}
    assert RoleClassifier.infer_role(row_pacer) == ROLE_PACE_BOWLER


def test_potential_score_age_curve():
    """Verifies that younger players receive larger development growth headroom."""
    # Prodigy aged 19.5
    teen_pot = PotentialScoreEngine.calculate_potential_score(age=19.5, measured_performance_index=70.0, sample_confidence=0.9)
    # Mature domestic player aged 31.0
    mature_pot = PotentialScoreEngine.calculate_potential_score(age=31.0, measured_performance_index=70.0, sample_confidence=0.9)

    assert teen_pot["age_growth_multiplier"] > mature_pot["age_growth_multiplier"]
    assert teen_pot["developmental_headroom"] > mature_pot["developmental_headroom"]
    assert teen_pot["projected_peak_potential"] > mature_pot["projected_peak_potential"]


def test_player_ranker_leaderboard(benchmark_data):
    """Verifies that PlayerRanker outputs a valid leaderboard sorted descending by Overall Scouting Score."""
    ranker = PlayerRanker()
    ranked = ranker.rank_players(benchmark_data)

    assert len(ranked) == len(benchmark_data)
    assert "overall_scouting_score" in ranked.columns
    assert "role_performance_score" in ranked.columns
    assert "projected_peak_potential" in ranked.columns
    assert "consistency_score" in ranked.columns

    # Check strictly monotonic descending order
    scores = ranked["overall_scouting_score"].tolist()
    assert scores == sorted(scores, reverse=True)


def test_sensitivity_analysis(benchmark_data):
    """Verifies that sensitivity analysis computes rank deltas and rank stability classifications."""
    ranker = PlayerRanker()
    sens_df = ranker.run_sensitivity_analysis(benchmark_data)

    assert len(sens_df) == len(benchmark_data)
    assert "rank_range" in sens_df.columns
    assert "rank_stability" in sens_df.columns
    assert all(sens_df["rank_range"] >= 0)


def test_top_10_recommendations(benchmark_data):
    """Verifies that RecommendationEngine generates 10 qualified uncapped candidates with complete dossiers."""
    rec_engine = RecommendationEngine()
    recs = rec_engine.generate_top_10_recommendations(benchmark_data, max_age=26.0)

    assert len(recs) == 10
    for idx, r in enumerate(recs):
        assert r["rank"] == idx + 1
        assert r["uncapped_status"] in ["Confirmed Uncapped", "Potentially Uncapped"]
        assert r["age"] <= 26.0
        assert "rr_squad_fit" in r
        assert "final_recommendation_rationale" in r
        assert "potential_value" in r
        assert "risk_assessment" in r
        assert len(r["strengths"]) >= 1
        assert len(r["weaknesses"]) >= 1
        assert r["requires_human_approval"] is True

