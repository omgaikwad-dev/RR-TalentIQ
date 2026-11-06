"""
RR TalentIQ - Batting Scouting Engine
Computes advanced batting intelligence, phase metrics, boundary dominance,
dot-ball suppression, sample-size confidence, and role-adjusted batting indices.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np


class BattingScoutingEngine:
    """
    Advanced batting analytics for domestic talent scouting.
    Evaluates strike efficiency, boundary power, dot-ball discipline, and sample reliability.
    """

    def __init__(self, min_balls_threshold: int = 50):
        self.min_balls_threshold = min_balls_threshold

    def calculate_batting_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates and enriches the dataframe with in-depth batting metrics.
        """
        b_df = df.copy()

        # Runs per innings
        b_df["runs_per_innings"] = np.where(
            b_df["innings_batted"] > 0,
            (b_df["runs"] / b_df["innings_batted"]).round(2),
            0.0
        )

        # Boundary balls percentage: (fours + sixes) / balls_faced * 100
        b_df["boundary_ball_pct"] = np.where(
            b_df["balls_faced"] > 0,
            (((b_df["fours"] + b_df["sixes"]) / b_df["balls_faced"]) * 100).round(2),
            0.0
        )

        # Four % and Six %
        b_df["four_pct"] = np.where(
            b_df["balls_faced"] > 0,
            ((b_df["fours"] / b_df["balls_faced"]) * 100).round(2),
            0.0
        )
        b_df["six_pct"] = np.where(
            b_df["balls_faced"] > 0,
            ((b_df["sixes"] / b_df["balls_faced"]) * 100).round(2),
            0.0
        )

        # Non-boundary strike rate (strike rotation efficiency)
        # Non-boundary runs = runs - (4s*4 + 6s*6)
        # Non-boundary balls = balls_faced - (4s + 6s)
        b_runs = (b_df["fours"] * 4) + (b_df["sixes"] * 6)
        nb_runs = np.maximum(0, b_df["runs"] - b_runs)
        nb_balls = np.maximum(1, b_df["balls_faced"] - (b_df["fours"] + b_df["sixes"]))
        b_df["rotation_strike_rate"] = np.where(
            b_df["balls_faced"] > 0,
            ((nb_runs / nb_balls) * 100).round(2),
            0.0
        )

        # Balls per dismissal (Balls faced / max(1, outs))
        est_outs = np.maximum(1, np.where(
            b_df["batting_average"] > 0,
            (b_df["runs"] / b_df["batting_average"]).round(0),
            b_df["innings_batted"]
        ))
        b_df["balls_per_dismissal"] = np.where(
            est_outs > 0,
            (b_df["balls_faced"] / est_outs).round(2),
            0.0
        )

        # Sample size confidence coefficient: logistic curve scaling from 0 to 1
        # Reaches 0.90+ confidence at ~300 balls faced
        k = 150.0
        b_df["sample_confidence_bat"] = (
            1.0 - np.exp(-b_df["balls_faced"] / k)
        ).round(3)

        # Batting Impact Index (BII)
        # Balanced formula rewarding Strike Rate (60%) and Average (40%), penalized for high dot-ball %
        # Normalized against typical T20 domestic benchmarks (SR benchmark 135, Avg benchmark 30)
        sr_ratio = b_df["strike_rate"] / 135.0
        avg_ratio = b_df["batting_average"] / 30.0
        dot_penalty = 1.0 - ((b_df["dot_ball_pct_bat"] - 30.0).clip(lower=0) / 100.0)
        
        raw_bii = (0.60 * sr_ratio + 0.40 * avg_ratio) * dot_penalty * 100.0
        # Discount by sample confidence to avoid rating a batter with 10 balls as top 1
        b_df["batting_impact_index"] = (raw_bii * b_df["sample_confidence_bat"]).round(2)

        return b_df

    def get_role_benchmark_comparison(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compares each batter against their role-specific peer group median.
        """
        metrics_df = self.calculate_batting_metrics(df)
        eligible = metrics_df[metrics_df["balls_faced"] >= self.min_balls_threshold].copy()
        
        role_medians = eligible.groupby("playing_role").agg(
            median_sr=("strike_rate", "median"),
            median_avg=("batting_average", "median"),
            median_boundary=("boundary_pct_bat", "median"),
            median_bii=("batting_impact_index", "median")
        ).reset_index()

        enriched = pd.merge(metrics_df, role_medians, on="playing_role", how="left")
        enriched["sr_vs_role_median"] = (enriched["strike_rate"] - enriched["median_sr"]).round(2)
        enriched["avg_vs_role_median"] = (enriched["batting_average"] - enriched["median_avg"]).round(2)
        enriched["bii_vs_role_median"] = (enriched["batting_impact_index"] - enriched["median_bii"]).round(2)
        return enriched

    def get_top_batting_prospects(
        self,
        df: pd.DataFrame,
        top_n: int = 10,
        max_age: Optional[float] = None,
        role: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieves top batting prospects sorted by Batting Impact Index and sample-size reliability.
        """
        analyzed = self.calculate_batting_metrics(df)
        if max_age is not None:
            analyzed = analyzed[(analyzed["age"].notnull()) & (analyzed["age"] <= max_age)]
        if role is not None and role != "All":
            analyzed = analyzed[analyzed["playing_role"] == role]
            
        ranked = analyzed.sort_values(by="batting_impact_index", ascending=False).head(top_n).reset_index(drop=True)
        ranked.index = ranked.index + 1
        return ranked

