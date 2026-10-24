"""
IPL Analytics Pro - Analytics Unit and Regression Tests
Validates calculations in SeasonAnalytics, TeamAnalytics, PlayerAnalytics, VenueAnalytics, MatchInsights.
"""

import os
import pytest
import pandas as pd
from analytics.season_analysis import SeasonAnalytics
from analytics.team_analysis import TeamAnalytics
from analytics.player_analysis import PlayerAnalytics
from analytics.venue_analysis import VenueAnalytics
from analytics.match_insights import MatchInsights

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

@pytest.fixture(scope="module")
def datasets():
    matches_path = os.path.join(PROCESSED_DIR, "matches_cleaned.csv")
    deliveries_path = os.path.join(PROCESSED_DIR, "deliveries_cleaned.parquet")
    
    assert os.path.exists(matches_path), f"Matches file missing: {matches_path}"
    assert os.path.exists(deliveries_path), f"Deliveries file missing: {deliveries_path}"
    
    df_m = pd.read_csv(matches_path)
    df_d = pd.read_parquet(deliveries_path)
    return df_m, df_d

def test_season_analytics(datasets):
    df_m, df_d = datasets
    sa = SeasonAnalytics(df_m, df_d)
    
    overview = sa.get_season_overview()
    assert overview["total_matches"] == 1243
    assert overview["total_runs"] > 350000
    assert overview["total_wickets"] > 14000
    assert overview["team_count"] >= 10
    
    trends = sa.get_yearly_trends()
    assert len(trends) == 19
    assert 2026 in trends["Season"].values
    
    standings_2024 = sa.get_season_standings(2024)
    assert len(standings_2024) == 10
    assert "Points" in standings_2024.columns

def test_team_analytics(datasets):
    df_m, df_d = datasets
    ta = TeamAnalytics(df_m, df_d)
    
    teams = ta.get_teams_list()
    assert len(teams) >= 10
    assert "Mumbai Indians" in teams
    assert "Chennai Super Kings" in teams
    
    all_summary = ta.get_all_teams_summary()
    assert len(all_summary) == len(teams)
    top_winner = all_summary.iloc[0]["Team"]
    assert top_winner in ["Mumbai Indians", "Chennai Super Kings"]
    
    h2h = ta.get_head_to_head("Mumbai Indians", "Chennai Super Kings")
    assert h2h["total_played"] >= 35
    assert h2h["team1_wins"] + h2h["team2_wins"] <= h2h["total_played"]

def test_player_analytics(datasets):
    df_m, df_d = datasets
    pa = PlayerAnalytics(df_m, df_d)
    
    top_batters = pa.get_top_run_scorers(10)
    assert len(top_batters) == 10
    assert "V Kohli" in top_batters["striker"].values
    
    top_bowlers = pa.get_top_wicket_takers(10)
    assert len(top_bowlers) == 10
    assert top_bowlers.iloc[0]["Wickets"] >= 170
    
    kohli_stats = pa.get_virat_kohli_analysis()
    assert kohli_stats["total_runs"] > 7000
    assert len(kohli_stats["yearly_trajectory"]) >= 15

def test_venue_analytics(datasets):
    df_m, df_d = datasets
    va = VenueAnalytics(df_m, df_d)
    
    venues_summary = va.get_venues_summary(min_matches=5)
    assert len(venues_summary) >= 15
    assert "Wankhede Stadium, Mumbai" in venues_summary["Venue"].values

def test_match_insights(datasets):
    df_m, df_d = datasets
    mi = MatchInsights(df_m, df_d)
    
    high_scoring = mi.get_highest_scoring_matches(5)
    assert len(high_scoring) == 5
    assert high_scoring.iloc[0]["total_match_runs"] >= 450
    
    high_ind = mi.get_highest_individual_scores(5)
    assert len(high_ind) == 5
    assert high_ind.iloc[0]["Runs"] >= 150
