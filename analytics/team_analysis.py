"""
IPL Analytics Pro - Team Analytics Module
Provides statistical functions for team performance, head-to-head comparisons, and toss win equity.
"""

import pandas as pd
import numpy as np

class TeamAnalytics:
    def __init__(self, matches_df: pd.DataFrame, deliveries_df: pd.DataFrame):
        self.matches = matches_df
        self.deliveries = deliveries_df

    def get_teams_list(self):
        """Returns sorted list of all standardized teams."""
        t1 = self.matches["team1"].dropna().unique()
        t2 = self.matches["team2"].dropna().unique()
        return sorted(list(set(t1) | set(t2)))

    def get_all_teams_summary(self):
        """Computes all-time summary for every team."""
        teams = self.get_teams_list()
        summary = []
        for t in teams:
            t_matches = self.matches[(self.matches["team1"] == t) | (self.matches["team2"] == t)]
            played = len(t_matches)
            won = len(self.matches[self.matches["winner"] == t])
            toss_won = len(self.matches[self.matches["toss_winner"] == t])
            toss_match_won = len(self.matches[(self.matches["toss_winner"] == t) & (self.matches["winner"] == t)])
            
            # Batting 1st vs chasing
            bat_first_played = len(t_matches[t_matches["batting_first_team"] == t])
            bat_first_won = len(t_matches[(t_matches["batting_first_team"] == t) & (t_matches["winner"] == t)])
            chase_played = len(t_matches[t_matches["chasing_team"] == t])
            chase_won = len(t_matches[(t_matches["chasing_team"] == t) & (t_matches["winner"] == t)])
            
            win_pct = round((won / played) * 100, 2) if played > 0 else 0.0
            bat_first_pct = round((bat_first_won / bat_first_played) * 100, 2) if bat_first_played > 0 else 0.0
            chase_pct = round((chase_won / chase_played) * 100, 2) if chase_played > 0 else 0.0
            toss_conversion_pct = round((toss_match_won / toss_won) * 100, 2) if toss_won > 0 else 0.0
            
            summary.append({
                "Team": t,
                "Matches": played,
                "Won": won,
                "Lost": played - won,
                "Win %": win_pct,
                "Bat 1st Won": bat_first_won,
                "Bat 1st Win %": bat_first_pct,
                "Chase Won": chase_won,
                "Chase Win %": chase_pct,
                "Toss Won": toss_won,
                "Toss Conversion %": toss_conversion_pct
            })
            
        df_res = pd.DataFrame(summary).sort_values(by=["Won", "Win %"], ascending=False).reset_index(drop=True)
        return df_res

    def get_team_season_breakdown(self, team: str):
        """Returns year-over-year match record for a specific team."""
        t_matches = self.matches[(self.matches["team1"] == team) | (self.matches["team2"] == team)]
        seasons = sorted(t_matches["season"].unique())
        
        breakdown = []
        for s in seasons:
            sm = t_matches[t_matches["season"] == s]
            played = len(sm)
            won = len(sm[sm["winner"] == team])
            win_pct = round((won / played) * 100, 1) if played > 0 else 0.0
            breakdown.append({
                "Season": s,
                "Matches": played,
                "Won": won,
                "Lost": played - won,
                "Win %": win_pct
            })
        return pd.DataFrame(breakdown)

    def get_head_to_head(self, team1: str, team2: str):
        """Computes comprehensive head-to-head record between two teams."""
        h2h_matches = self.matches[
            ((self.matches["team1"] == team1) & (self.matches["team2"] == team2)) |
            ((self.matches["team1"] == team2) & (self.matches["team2"] == team1))
        ].copy()
        
        total_played = len(h2h_matches)
        t1_wins = len(h2h_matches[h2h_matches["winner"] == team1])
        t2_wins = len(h2h_matches[h2h_matches["winner"] == team2])
        no_res = len(h2h_matches[h2h_matches["result_type"] == "no_result"])
        ties = len(h2h_matches[h2h_matches["result_type"] == "tie_super_over"])
        
        # Scoring head-to-head
        t1_scores = []
        t2_scores = []
        for _, row in h2h_matches.iterrows():
            if row["team1"] == team1:
                t1_scores.append(row["team1_score"])
                t2_scores.append(row["team2_score"])
            else:
                t1_scores.append(row["team2_score"])
                t2_scores.append(row["team1_score"])
                
        avg_score_t1 = round(np.mean([s for s in t1_scores if s > 0]), 1) if t1_scores else 0
        avg_score_t2 = round(np.mean([s for s in t2_scores if s > 0]), 1) if t2_scores else 0
        
        return {
            "team1": team1,
            "team2": team2,
            "total_played": total_played,
            "team1_wins": t1_wins,
            "team2_wins": t2_wins,
            "no_results": no_res,
            "ties_super_overs": ties,
            "team1_win_pct": round((t1_wins / total_played) * 100, 1) if total_played > 0 else 0.0,
            "team2_win_pct": round((t2_wins / total_played) * 100, 1) if total_played > 0 else 0.0,
            "team1_avg_score": avg_score_t1,
            "team2_avg_score": avg_score_t2,
            "matches_list": h2h_matches[["match_id", "season", "date", "venue", "toss_winner", "toss_decision", "winner", "result_type", "win_by_runs", "win_by_wickets", "player_of_match"]]
        }
