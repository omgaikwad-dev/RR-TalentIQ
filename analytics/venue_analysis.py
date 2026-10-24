"""
IPL Analytics Pro - Venue Analytics Module
Provides statistical functions for stadium usage, pitch characteristics, average scores, and win equity.
"""

import pandas as pd
import numpy as np

class VenueAnalytics:
    def __init__(self, matches_df: pd.DataFrame, deliveries_df: pd.DataFrame):
        self.matches = matches_df
        self.deliveries = deliveries_df

    def get_venues_list(self):
        """Returns list of standardized venues sorted by total matches hosted."""
        return self.matches["venue"].value_counts().index.tolist()

    def get_venues_summary(self, min_matches: int = 5):
        """Computes comprehensive metrics for stadiums hosting at least min_matches."""
        venues = self.matches["venue"].value_counts()
        qual_venues = venues[venues >= min_matches].index
        
        summary = []
        for v in qual_venues:
            v_matches = self.matches[self.matches["venue"] == v]
            matches_count = len(v_matches)
            
            # Scores
            first_inn_scores = v_matches[v_matches["team1_score"] > 0]["team1_score"]
            second_inn_scores = v_matches[v_matches["team2_score"] > 0]["team2_score"]
            
            avg_1st_inn = round(first_inn_scores.mean(), 1) if len(first_inn_scores) > 0 else 0
            avg_2nd_inn = round(second_inn_scores.mean(), 1) if len(second_inn_scores) > 0 else 0
            highest_total = int(max(first_inn_scores.max() if len(first_inn_scores) else 0,
                                    second_inn_scores.max() if len(second_inn_scores) else 0))
            lowest_total = int(min(first_inn_scores[first_inn_scores > 30].min() if len(first_inn_scores[first_inn_scores > 30]) else 999,
                                   second_inn_scores[second_inn_scores > 30].min() if len(second_inn_scores[second_inn_scores > 30]) else 999))
            if lowest_total == 999:
                lowest_total = 0
                
            # Bat 1st vs Chase
            bat_1st_wins = len(v_matches[v_matches["batting_first_win"] == 1])
            chase_wins = len(v_matches[v_matches["chasing_win"] == 1])
            ties = len(v_matches[v_matches["result_type"] == "tie_super_over"])
            
            bat_1st_pct = round((bat_1st_wins / matches_count) * 100, 1) if matches_count > 0 else 0.0
            chase_pct = round((chase_wins / matches_count) * 100, 1) if matches_count > 0 else 0.0
            
            summary.append({
                "Venue": v,
                "Matches": matches_count,
                "Avg 1st Inn Score": avg_1st_inn,
                "Avg 2nd Inn Score": avg_2nd_inn,
                "Bat 1st Wins": bat_1st_wins,
                "Bat 1st Win %": bat_1st_pct,
                "Chase Wins": chase_wins,
                "Chase Win %": chase_pct,
                "Ties": ties,
                "Highest Score": highest_total,
                "Lowest Defended": lowest_total
            })
            
        df_res = pd.DataFrame(summary).sort_values("Matches", ascending=False).reset_index(drop=True)
        return df_res

    def get_venue_details(self, venue_name: str):
        """Detailed deep-dive metrics for a single stadium."""
        v_matches = self.matches[self.matches["venue"] == venue_name]
        v_deliv = self.deliveries[self.deliveries["venue"] == venue_name]
        
        total_runs = int(v_deliv["total_runs"].sum())
        total_wickets = int(v_deliv["is_wicket"].sum())
        total_sixes = int(v_deliv["is_boundary_six"].sum())
        total_fours = int(v_deliv["is_boundary_four"].sum())
        
        # Most successful team at venue
        winner_counts = v_matches[v_matches["winner"] != "No Result"]["winner"].value_counts()
        top_team = winner_counts.index[0] if len(winner_counts) > 0 else "N/A"
        top_team_wins = int(winner_counts.values[0]) if len(winner_counts) > 0 else 0
        
        # Highest match totals
        highest_matches = v_matches.sort_values("team1_score", ascending=False)[
            ["date", "season", "team1", "team2", "team1_score", "team2_score", "winner", "player_of_match"]
        ].head(5)
        
        return {
            "venue": venue_name,
            "total_matches": len(v_matches),
            "total_runs": total_runs,
            "total_wickets": total_wickets,
            "total_sixes": total_sixes,
            "total_fours": total_fours,
            "top_team": top_team,
            "top_team_wins": top_team_wins,
            "highest_matches": highest_matches
        }
