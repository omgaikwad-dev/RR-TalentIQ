"""
IPL Analytics Pro - Player Analytics Module
Provides statistical functions for batting leaders, bowling leaders, player vs player head-to-head,
and specialized player deep dives (e.g. Virat Kohli).
"""

import pandas as pd
import numpy as np

class PlayerAnalytics:
    def __init__(self, matches_df: pd.DataFrame, deliveries_df: pd.DataFrame):
        self.matches = matches_df
        # Exclude super overs for official career statistics
        self.deliveries = deliveries_df[deliveries_df["is_super_over"] == 0].copy()

    def get_top_run_scorers(self, n: int = 10, season: int = None):
        """Calculates top run scorers across all seasons or in a specific season."""
        df = self.deliveries if season is None else self.deliveries[self.deliveries["season"] == season]
        
        # Batting stats
        bat_agg = df.groupby("striker").agg(
            Runs=("runs_off_bat", "sum"),
            Balls=("is_legal_delivery", "sum"),
            Fours=("is_boundary_four", "sum"),
            Sixes=("is_boundary_six", "sum"),
            Innings=("match_id", "nunique")
        ).reset_index()
        
        # Outs
        outs_df = df[df["player_dismissed"].notnull()]["player_dismissed"].value_counts()
        bat_agg["Outs"] = bat_agg["striker"].map(outs_df).fillna(0).astype(int)
        
        bat_agg["Strike_Rate"] = ((bat_agg["Runs"] / bat_agg["Balls"].replace(0, np.nan)) * 100).round(2).fillna(0.0)
        bat_agg["Average"] = (bat_agg["Runs"] / bat_agg["Outs"].replace(0, 1)).round(2)
        
        # Calculate 50s and 100s
        match_scores = df.groupby(["match_id", "striker"])["runs_off_bat"].sum().reset_index()
        fifties = match_scores[(match_scores["runs_off_bat"] >= 50) & (match_scores["runs_off_bat"] < 100)].groupby("striker")["match_id"].count()
        hundreds = match_scores[match_scores["runs_off_bat"] >= 100].groupby("striker")["match_id"].count()
        high_score = match_scores.groupby("striker")["runs_off_bat"].max()
        
        bat_agg["Fifties"] = bat_agg["striker"].map(fifties).fillna(0).astype(int)
        bat_agg["Hundreds"] = bat_agg["striker"].map(hundreds).fillna(0).astype(int)
        bat_agg["High_Score"] = bat_agg["striker"].map(high_score).fillna(0).astype(int)
        
        sorted_bat = bat_agg.sort_values(by=["Runs", "Average"], ascending=False).head(n).reset_index(drop=True)
        sorted_bat.index = sorted_bat.index + 1
        return sorted_bat

    def get_top_wicket_takers(self, n: int = 10, season: int = None):
        """Calculates top wicket-takers (bowler-credited wickets only)."""
        df = self.deliveries if season is None else self.deliveries[self.deliveries["season"] == season]
        
        bowl_agg = df.groupby("bowler").agg(
            Wickets=("is_bowler_wicket", "sum"),
            Runs_Conceded=("bowler_runs_conceded", "sum"),
            Balls=("is_legal_delivery", "sum"),
            Innings=("match_id", "nunique")
        ).reset_index()
        
        bowl_agg["Overs"] = (bowl_agg["Balls"] // 6) + ((bowl_agg["Balls"] % 6) / 10)
        bowl_agg["Economy"] = ((bowl_agg["Runs_Conceded"] / (bowl_agg["Balls"].replace(0, np.nan) / 6))).round(2).fillna(0.0)
        bowl_agg["Average"] = ((bowl_agg["Runs_Conceded"] / bowl_agg["Wickets"].replace(0, np.nan))).round(2).fillna(0.0)
        bowl_agg["Strike_Rate"] = ((bowl_agg["Balls"] / bowl_agg["Wickets"].replace(0, np.nan))).round(2).fillna(0.0)
        
        # Best bowling in a match
        match_bowl = df.groupby(["match_id", "bowler"]).agg(
            Wkts=("is_bowler_wicket", "sum"),
            Runs=("bowler_runs_conceded", "sum")
        ).reset_index()
        match_bowl["sort_key"] = match_bowl["Wkts"] * 1000 - match_bowl["Runs"]
        best_figures = match_bowl.sort_values("sort_key", ascending=False).groupby("bowler").first()
        best_str = best_figures.apply(lambda r: f"{int(r['Wkts'])}/{int(r['Runs'])}", axis=1)
        bowl_agg["BBI"] = bowl_agg["bowler"].map(best_str).fillna("0/0")
        
        sorted_bowl = bowl_agg.sort_values(by=["Wickets", "Economy"], ascending=[False, True]).head(n).reset_index(drop=True)
        sorted_bowl.index = sorted_bowl.index + 1
        return sorted_bowl

    def get_player_season_trajectory(self, player_name: str):
        """Computes season-by-season batting and bowling performance for any player."""
        bat_df = self.deliveries[self.deliveries["striker"] == player_name]
        bowl_df = self.deliveries[self.deliveries["bowler"] == player_name]
        
        all_seasons = sorted(list(set(bat_df["season"].unique()) | set(bowl_df["season"].unique())))
        
        records = []
        for s in all_seasons:
            s_bat = bat_df[bat_df["season"] == s]
            s_bowl = bowl_df[bowl_df["season"] == s]
            
            runs = int(s_bat["runs_off_bat"].sum())
            balls = int(s_bat["is_legal_delivery"].sum())
            outs = int(self.deliveries[(self.deliveries["season"] == s) & (self.deliveries["player_dismissed"] == player_name)]["player_dismissed"].count())
            sr = round((runs / balls * 100), 2) if balls > 0 else 0.0
            avg = round((runs / outs), 2) if outs > 0 else (runs if runs > 0 else 0.0)
            fours = int(s_bat["is_boundary_four"].sum())
            sixes = int(s_bat["is_boundary_six"].sum())
            
            wkts = int(s_bowl["is_bowler_wicket"].sum())
            rc = int(s_bowl["bowler_runs_conceded"].sum())
            b_balls = int(s_bowl["is_legal_delivery"].sum())
            econ = round((rc / (b_balls / 6)), 2) if b_balls > 0 else 0.0
            
            records.append({
                "Season": s,
                "Runs": runs,
                "Balls": balls,
                "Outs": outs,
                "Average": avg,
                "Strike Rate": sr,
                "4s": fours,
                "6s": sixes,
                "Wickets": wkts,
                "Economy": econ
            })
        return pd.DataFrame(records)

    def get_batter_vs_bowler(self, batter: str, bowler: str):
        """Head-to-head match-up statistics between a batter and bowler."""
        matchup = self.deliveries[(self.deliveries["striker"] == batter) & (self.deliveries["bowler"] == bowler)]
        
        balls = len(matchup[matchup["is_legal_delivery"] == 1])
        runs = int(matchup["runs_off_bat"].sum())
        dismissals = int((matchup["player_dismissed"] == batter).sum())
        dots = int(((matchup["runs_off_bat"] == 0) & (matchup["is_legal_delivery"] == 1)).sum())
        fours = int(matchup["is_boundary_four"].sum())
        sixes = int(matchup["is_boundary_six"].sum())
        
        strike_rate = round((runs / balls * 100), 2) if balls > 0 else 0.0
        dot_pct = round((dots / balls * 100), 1) if balls > 0 else 0.0
        
        return {
            "batter": batter,
            "bowler": bowler,
            "balls": balls,
            "runs": runs,
            "dismissals": dismissals,
            "dots": dots,
            "dot_pct": dot_pct,
            "fours": fours,
            "sixes": sixes,
            "strike_rate": strike_rate
        }

    def get_virat_kohli_analysis(self):
        """Specialized deep dive analytics for Virat Kohli."""
        kohli_df = self.deliveries[self.deliveries["striker"] == "V Kohli"]
        total_runs = int(kohli_df["runs_off_bat"].sum())
        total_balls = int(kohli_df["is_legal_delivery"].sum())
        total_fours = int(kohli_df["is_boundary_four"].sum())
        total_sixes = int(kohli_df["is_boundary_six"].sum())
        
        outs = int((self.deliveries["player_dismissed"] == "V Kohli").sum())
        avg = round(total_runs / outs, 2) if outs > 0 else total_runs
        sr = round(total_runs / total_balls * 100, 2) if total_balls > 0 else 0.0
        
        # Phase performance
        phase_stats = kohli_df.groupby("phase").agg(
            Runs=("runs_off_bat", "sum"),
            Balls=("is_legal_delivery", "sum"),
            Fours=("is_boundary_four", "sum"),
            Sixes=("is_boundary_six", "sum")
        ).reset_index()
        phase_stats["Strike_Rate"] = ((phase_stats["Runs"] / phase_stats["Balls"]) * 100).round(2)
        
        # Opponent performance
        opp_stats = kohli_df.groupby("bowling_team").agg(
            Runs=("runs_off_bat", "sum"),
            Balls=("is_legal_delivery", "sum"),
            Fours=("is_boundary_four", "sum"),
            Sixes=("is_boundary_six", "sum")
        ).reset_index().sort_values("Runs", ascending=False)
        opp_stats["Strike_Rate"] = ((opp_stats["Runs"] / opp_stats["Balls"]) * 100).round(2)
        
        # Yearly progression
        yearly = self.get_player_season_trajectory("V Kohli")
        
        return {
            "player": "Virat Kohli",
            "total_runs": total_runs,
            "balls_faced": total_balls,
            "batting_average": avg,
            "strike_rate": sr,
            "fours": total_fours,
            "sixes": total_sixes,
            "phase_breakdown": phase_stats,
            "opponent_breakdown": opp_stats,
            "yearly_trajectory": yearly
        }
