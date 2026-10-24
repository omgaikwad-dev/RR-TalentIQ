"""
IPL Analytics Pro - Match Insights Module
Provides statistical functions for all-time records, highest-scoring matches, closest finishes,
largest victories, and individual record masteries.
"""

import pandas as pd
import numpy as np

class MatchInsights:
    def __init__(self, matches_df: pd.DataFrame, deliveries_df: pd.DataFrame):
        self.matches = matches_df
        self.deliveries = deliveries_df

    def get_highest_scoring_matches(self, n: int = 10):
        """Finds highest aggregate match scores in IPL history."""
        m_df = self.matches.copy()
        m_df["total_match_runs"] = m_df["team1_score"] + m_df["team2_score"]
        
        top_matches = m_df[m_df["total_match_runs"] > 0].sort_values("total_match_runs", ascending=False).head(n)
        return top_matches[[
            "season", "date", "team1", "team2", "team1_score", "team2_score", "total_match_runs", "winner", "venue"
        ]].reset_index(drop=True)

    def get_highest_innings_totals(self, n: int = 10):
        """Finds highest individual team totals in an innings."""
        reg_d = self.deliveries[self.deliveries["is_super_over"] == 0]
        inn_totals = reg_d.groupby(["match_id", "innings", "batting_team", "bowling_team", "season", "venue"]).agg(
            Score=("total_runs", "sum"),
            Wickets=("is_wicket", "sum")
        ).reset_index()
        
        inn_totals["Match_Score"] = inn_totals.apply(lambda r: f"{r['Score']}/{r['Wickets']}", axis=1)
        top_inn = inn_totals.sort_values("Score", ascending=False).head(n).reset_index(drop=True)
        top_inn.index = top_inn.index + 1
        return top_inn[["season", "batting_team", "bowling_team", "Score", "Wickets", "Match_Score", "venue"]]

    def get_largest_margins_by_runs(self, n: int = 10):
        """Finds largest victories by runs."""
        top_runs = self.matches[self.matches["win_by_runs"] > 0].sort_values("win_by_runs", ascending=False).head(n)
        return top_runs[[
            "season", "date", "winner", "team1", "team2", "win_by_runs", "venue", "player_of_match"
        ]].reset_index(drop=True)

    def get_closest_finishes(self, n: int = 15):
        """Finds 1-run wins, last-ball finishes, and super overs."""
        one_run_wins = self.matches[self.matches["win_by_runs"] == 1].copy()
        one_run_wins["margin_desc"] = "Won by 1 run"
        
        super_overs = self.matches[self.matches["result_type"] == "tie_super_over"].copy()
        super_overs["margin_desc"] = "Tied (Won via Super Over)"
        
        one_wicket_wins = self.matches[self.matches["win_by_wickets"] == 1].copy()
        one_wicket_wins["margin_desc"] = "Won by 1 wicket"
        
        closest = pd.concat([one_run_wins, super_overs, one_wicket_wins]).sort_values("date", ascending=False).head(n)
        return closest[[
            "season", "date", "winner", "team1", "team2", "margin_desc", "venue", "player_of_match"
        ]].reset_index(drop=True)

    def get_highest_individual_scores(self, n: int = 10):
        """Finds top individual batting innings scores in IPL history."""
        reg_d = self.deliveries[self.deliveries["is_super_over"] == 0]
        
        ind_bat = reg_d.groupby(["match_id", "striker", "batting_team", "bowling_team", "season"]).agg(
            Runs=("runs_off_bat", "sum"),
            Balls=("is_legal_delivery", "sum"),
            Fours=("is_boundary_four", "sum"),
            Sixes=("is_boundary_six", "sum")
        ).reset_index()
        
        ind_bat["Strike_Rate"] = ((ind_bat["Runs"] / ind_bat["Balls"]) * 100).round(2)
        top_scores = ind_bat.sort_values(by=["Runs", "Strike_Rate"], ascending=False).head(n).reset_index(drop=True)
        top_scores.index = top_scores.index + 1
        return top_scores[["striker", "Runs", "Balls", "Strike_Rate", "Fours", "Sixes", "batting_team", "bowling_team", "season"]]

    def get_best_bowling_figures(self, n: int = 10):
        """Finds top individual bowling figures in an innings."""
        reg_d = self.deliveries[self.deliveries["is_super_over"] == 0]
        
        ind_bowl = reg_d.groupby(["match_id", "bowler", "bowling_team", "batting_team", "season"]).agg(
            Wickets=("is_bowler_wicket", "sum"),
            Runs_Conceded=("bowler_runs_conceded", "sum"),
            Balls=("is_legal_delivery", "sum")
        ).reset_index()
        
        ind_bowl["Overs"] = (ind_bowl["Balls"] // 6) + ((ind_bowl["Balls"] % 6) / 10)
        ind_bowl["Figures"] = ind_bowl.apply(lambda r: f"{r['Wickets']}/{r['Runs_Conceded']}", axis=1)
        ind_bowl["sort_key"] = ind_bowl["Wickets"] * 1000 - ind_bowl["Runs_Conceded"]
        
        top_bowl = ind_bowl.sort_values("sort_key", ascending=False).head(n).reset_index(drop=True)
        top_bowl.index = top_bowl.index + 1
        return top_bowl[["bowler", "Figures", "Overs", "Wickets", "Runs_Conceded", "bowling_team", "batting_team", "season"]]
