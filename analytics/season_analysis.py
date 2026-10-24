"""
IPL Analytics Pro - Season Analytics Module
Provides statistical functions for season-level trends, year-over-year metrics, and season standings.
"""

import pandas as pd
import numpy as np

class SeasonAnalytics:
    def __init__(self, matches_df: pd.DataFrame, deliveries_df: pd.DataFrame):
        self.matches = matches_df
        self.deliveries = deliveries_df

    def get_seasons_list(self):
        """Returns sorted list of available seasons."""
        return sorted(self.matches["season"].dropna().unique().tolist())

    def get_season_overview(self, season=None):
        """Computes summary KPI metrics for all seasons or a specific season."""
        m_df = self.matches if season is None else self.matches[self.matches["season"] == season]
        d_df = self.deliveries if season is None else self.deliveries[self.deliveries["season"] == season]
        reg_d = d_df[d_df["is_super_over"] == 0]

        total_matches = len(m_df)
        total_runs = int(d_df["total_runs"].sum())
        total_wickets = int(d_df["is_wicket"].sum())
        total_fours = int(d_df["is_boundary_four"].sum())
        total_sixes = int(d_df["is_boundary_six"].sum())
        
        valid_matches = m_df[m_df["team1_score"] > 0]
        avg_runs_per_match = round(total_runs / total_matches, 1) if total_matches > 0 else 0
        avg_1st_inn = round(valid_matches["team1_score"].mean(), 1) if len(valid_matches) > 0 else 0
        
        teams_participated = sorted(list(set(m_df["team1"].dropna().unique()) | set(m_df["team2"].dropna().unique())))
        
        # Bat 1st vs chase
        bat_first_wins = int(m_df["batting_first_win"].sum())
        chase_wins = int(m_df["chasing_win"].sum())
        ties = int((m_df["result_type"] == "tie_super_over").sum())
        no_results = int((m_df["result_type"] == "no_result").sum())

        return {
            "season": "All Seasons (2008–2026)" if season is None else f"Season {season}",
            "total_matches": total_matches,
            "total_runs": total_runs,
            "total_wickets": total_wickets,
            "total_fours": total_fours,
            "total_sixes": total_sixes,
            "avg_runs_per_match": avg_runs_per_match,
            "avg_first_innings_score": avg_1st_inn,
            "team_count": len(teams_participated),
            "teams": teams_participated,
            "bat_first_wins": bat_first_wins,
            "chase_wins": chase_wins,
            "ties": ties,
            "no_results": no_results,
        }

    def get_yearly_trends(self):
        """Generates season-by-season time series comparison table."""
        records = []
        for s in self.get_seasons_list():
            ov = self.get_season_overview(season=s)
            records.append({
                "Season": s,
                "Matches": ov["total_matches"],
                "Total Runs": ov["total_runs"],
                "Avg Runs/Match": ov["avg_runs_per_match"],
                "Avg 1st Inn Score": ov["avg_first_innings_score"],
                "Fours": ov["total_fours"],
                "Sixes": ov["total_sixes"],
                "Total Wickets": ov["total_wickets"],
                "Teams Count": ov["team_count"],
                "Bat 1st Wins": ov["bat_first_wins"],
                "Chase Wins": ov["chase_wins"],
            })
        return pd.DataFrame(records)

    def get_season_standings(self, season: int):
        """Calculates official points table and win/loss records for a selected season."""
        m_df = self.matches[self.matches["season"] == season]
        teams = sorted(list(set(m_df["team1"].dropna().unique()) | set(m_df["team2"].dropna().unique())))
        
        table = []
        for t in teams:
            t_matches = m_df[(m_df["team1"] == t) | (m_df["team2"] == t)]
            played = len(t_matches)
            won = len(m_df[m_df["winner"] == t])
            no_res = len(t_matches[t_matches["result_type"] == "no_result"])
            lost = played - won - no_res
            pts = (won * 2) + (no_res * 1)
            win_pct = round((won / played) * 100, 1) if played > 0 else 0.0
            
            table.append({
                "Team": t,
                "Matches": played,
                "Won": won,
                "Lost": lost,
                "No Result": no_res,
                "Points": pts,
                "Win %": win_pct
            })
            
        df_table = pd.DataFrame(table).sort_values(by=["Points", "Win %", "Won"], ascending=False).reset_index(drop=True)
        df_table.index = df_table.index + 1
        return df_table
