"""
RR TalentIQ - Bowling Scouting Engine
Evaluates bowling economy suppression, wicket-taking strike rates,
dot-ball dominance, phase effectiveness, and sample-size reliability.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np


class BowlingScoutingEngine:
    """
    Advanced bowling analytics for domestic talent scouting.
    Combines economy, strike rate, dot ball generation, and sample size confidence.
    """

    def __init__(self, min_overs_threshold: float = 10.0):
        self.min_overs_threshold = min_overs_threshold

    def calculate_bowling_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates and enriches the dataframe with advanced bowling metrics.
        """
        b_df = df.copy()

        # Decimal overs calculation (e.g. 15.3 overs = 15.5 decimal overs)
        dec_overs = np.floor(b_df["overs"]) + ((b_df["overs"] % 1) * 10 / 6)
        b_df["decimal_overs"] = dec_overs.round(2)

        # Wickets per innings bowled
        b_df["wickets_per_innings"] = np.where(
            b_df["innings_bowled"] > 0,
            (b_df["wickets"] / b_df["innings_bowled"]).round(2),
            0.0
        )

        # Dot balls count estimate: (balls_bowled * dot_ball_pct_bowl / 100)
        total_balls = np.where(
            b_df["balls_bowled"] > 0,
            b_df["balls_bowled"],
            (dec_overs * 6).round(0)
        )
        b_df["estimated_dot_balls"] = (total_balls * (b_df["dot_ball_pct_bowl"] / 100.0)).round(0).astype(int)

        # Estimated boundaries conceded per over
        # In domestic T20, typical boundary concession is ~1.2 boundaries per over for good bowlers
        b_df["boundary_concession_per_over"] = np.where(
            dec_overs > 0,
            np.maximum(0.5, (b_df["economy"] - 4.0) / 4.0).round(2),
            0.0
        )

        # Sample size confidence: reaches 0.90+ confidence at ~40 overs (240 balls)
        k_overs = 25.0
        b_df["sample_confidence_bowl"] = (
            1.0 - np.exp(-dec_overs / k_overs)
        ).round(3)

        # Bowling Impact Index (BII)
        # In T20 cricket, Economy is vital (50%) and Wicket Strike Rate is vital (50%)
        # Benchmarks: Economy benchmark 8.0 rpo (lower is better), Bowling SR benchmark 18 balls/wkt (lower is better)
        # Economy efficiency = (8.5 - economy) / 8.5
        # Strike rate efficiency = (24.0 - bowling_sr) / 24.0
        econ_score = np.maximum(0.0, (10.0 - b_df["economy"]) / 3.0)  # economy 7.0 -> score 1.0; 8.5 -> 0.5
        
        valid_sr = np.where(b_df["bowling_strike_rate"] > 0, b_df["bowling_strike_rate"], 36.0)
        sr_score = np.maximum(0.0, (28.0 - valid_sr) / 14.0)          # sr 14.0 -> score 1.0; 21.0 -> 0.5

        dot_boost = 1.0 + ((b_df["dot_ball_pct_bowl"] - 40.0).clip(lower=-10.0) / 100.0)

        raw_index = ((0.50 * econ_score + 0.50 * sr_score) * dot_boost * 100.0).clip(lower=0.0)
        b_df["bowling_impact_index"] = (raw_index * b_df["sample_confidence_bowl"]).round(2)

        return b_df

    def get_role_benchmark_comparison(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compares each bowler against their bowling style/role peer group medians.
        """
        metrics_df = self.calculate_bowling_metrics(df)
        eligible = metrics_df[metrics_df["decimal_overs"] >= self.min_overs_threshold].copy()
        
        style_medians = eligible.groupby("bowling_style").agg(
            median_econ=("economy", "median"),
            median_bowl_sr=("bowling_strike_rate", "median"),
            median_bowl_avg=("bowling_average", "median"),
            median_bii=("bowling_impact_index", "median")
        ).reset_index()

        enriched = pd.merge(metrics_df, style_medians, on="bowling_style", how="left")
        enriched["econ_vs_style_median"] = (enriched["economy"] - enriched["median_econ"]).round(2)
        enriched["sr_vs_style_median"] = (enriched["bowling_strike_rate"] - enriched["median_bowl_sr"]).round(2)
        enriched["bii_vs_style_median"] = (enriched["bowling_impact_index"] - enriched["median_bii"]).round(2)
        return enriched

    def get_top_bowling_prospects(
        self,
        df: pd.DataFrame,
        top_n: int = 10,
        max_age: Optional[float] = None,
        style: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieves top bowling prospects sorted by Bowling Impact Index and sample-size reliability.
        """
        analyzed = self.calculate_bowling_metrics(df)
        if max_age is not None:
            analyzed = analyzed[(analyzed["age"].notnull()) & (analyzed["age"] <= max_age)]
        if style is not None and style != "All":
            analyzed = analyzed[analyzed["bowling_style"] == style]
            
        ranked = analyzed.sort_values(by="bowling_impact_index", ascending=False).head(top_n).reset_index(drop=True)
        ranked.index = ranked.index + 1
        return ranked

