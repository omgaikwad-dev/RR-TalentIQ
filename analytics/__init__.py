"""
IPL Analytics Pro - Analytics Package
Provides modular statistical engines for Season, Team, Player, Venue, and Match analytics.
"""

from .season_analysis import SeasonAnalytics
from .team_analysis import TeamAnalytics
from .player_analysis import PlayerAnalytics
from .venue_analysis import VenueAnalytics
from .match_insights import MatchInsights

__all__ = [
    "SeasonAnalytics",
    "TeamAnalytics",
    "PlayerAnalytics",
    "VenueAnalytics",
    "MatchInsights",
]
