"""
RR TalentIQ - Unit Tests for Rajasthan Royals Squad & Auction Intelligence
Validates RR squad depth evaluation, squad requirement scoring,
valuation models, scarcity factors, and auction strategy quadrants.
"""

import pytest
import pandas as pd
from auction.rr_squad_analysis import RRSquadAnalyzer
from auction.squad_requirements import SquadRequirementsEngine
from auction.player_valuation import PlayerValuationEngine
from auction.auction_strategy import AuctionStrategyEngine
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.player_ranker import PlayerRanker


@pytest.fixture
def sample_player():
    return {
        "player_name": "Prodigy Pacer",
        "playing_role": "Pace Bowler",
        "age": 21.5,
        "overall_scouting_score": 82.5,
        "squad_fit_score": 88.0,
        "strike_rate": 100.0,
        "economy": 7.30,
        "bowling_strike_rate": 13.5
    }


def test_rr_squad_analysis_depth():
    """Verifies that RR core squad contains verified players and all 7 departments are audited."""
    core = RRSquadAnalyzer.get_core_squad()
    assert len(core) >= 10
    assert "Sanju Samson" in core["player_name"].values
    assert "Yashasvi Jaiswal" in core["player_name"].values

    depth = RRSquadAnalyzer.evaluate_department_depth()
    assert len(depth) == 7
    assert "Pace Bowling Department" in depth
    assert "All-Rounders Department" in depth
    assert depth["All-Rounders Department"]["gap_severity"] == "Critical Priority"


def test_squad_requirements_scoring(sample_player):
    """Verifies that high-priority young pacer receives a high squad fit score."""
    fit_score = SquadRequirementsEngine.calculate_squad_fit_score(sample_player)
    assert fit_score >= 85.0


def test_player_valuation_engine(sample_player):
    """Verifies that estimated market value and max bid ceilings are computed with scarcity multipliers."""
    val = PlayerValuationEngine.estimate_player_valuation(sample_player)
    assert val["base_price_lakhs"] == 30.0
    assert val["estimated_market_value_lakhs"] > 30.0
    assert val["max_recommended_bid_lakhs"] > val["estimated_market_value_lakhs"]
    assert val["is_unverified_estimate"] is True
    assert val["role_scarcity_multiplier"] == 1.40  # Pace Bowler scarcity factor


def test_auction_strategy_quadrants():
    """Verifies that players are successfully assigned into one of 4 auction strategy quadrants."""
    loader = DomesticDataLoader()
    raw = loader.get_benchmarked_uncapped_talents()
    ranker = PlayerRanker()
    scored = ranker.rank_players(raw)

    quad_df = AuctionStrategyEngine.classify_value_vs_cost_quadrants(scored)
    assert "auction_quadrant" in quad_df.columns
    assert "strategic_action" in quad_df.columns
    assert quad_df["auction_quadrant"].nunique() >= 2

    # Verify target auction cart can be assembled within budget
    cart = AuctionStrategyEngine.assemble_target_auction_cart(quad_df, budget_limit_lakhs=1400.0, max_picks=5)
    assert len(cart) >= 3
    assert all("max_bid_lakhs" in c for c in cart)

