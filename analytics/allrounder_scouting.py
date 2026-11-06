"""
RR TalentIQ - All-Rounder & Wicketkeeper Analysis Engine
Provides independent two-way discipline evaluation for all-rounders
and integrated batting-plus-glovework analysis for wicketkeepers.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from analytics.batting_scouting import BattingScoutingEngine
from analytics.bowling_scouting import BowlingScoutingEngine


class DualDisciplineScoutingEngine:
    """
    Evaluates multi-skilled cricketers without cross-subsidizing weaknesses.
    Applies independent discipline gating and glovework efficiency indexing.
    """

    def __init__(self):
        self.batting_engine = BattingScoutingEngine()
        self.bowling_engine = BowlingScoutingEngine()

    def evaluate_allrounders(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes independent batting and bowling indices, checks balance,
        and derives a composite all-rounder score that penalizes one-dimensional skew.
        """
        # Step 1: Compute independent discipline metrics
        bat_df = self.batting_engine.calculate_batting_metrics(df)
        bowl_df = self.bowling_engine.calculate_bowling_metrics(bat_df)
        
        ar_df = bowl_df.copy()

        # Minimum participation thresholds for legitimate all-rounders
        min_balls_bat = 60
        min_overs_bowl = 10.0

        has_bat_contribution = ar_df["balls_faced"] >= min_balls_bat
        has_bowl_contribution = ar_df["overs"] >= min_overs_bowl
        
        # Balance ratio: min(bat_index, bowl_index) / max(bat_index, bowl_index)
        bat_idx = ar_df["batting_impact_index"]
        bowl_idx = ar_df["bowling_impact_index"]

        max_idx = np.maximum(bat_idx, bowl_idx).replace(0, 1.0)
        min_idx = np.minimum(bat_idx, bowl_idx)
        balance_ratio = (min_idx / max_idx).round(3)
        ar_df["discipline_balance_ratio"] = balance_ratio

        # Harmonic composite score to strictly forbid one discipline hiding the other:
        # Harmonic Mean = 2 * (Bat * Bowl) / (Bat + Bowl + 1e-5)
        harmonic_score = np.where(
            (has_bat_contribution) & (has_bowl_contribution),
            (2.0 * bat_idx * bowl_idx) / (bat_idx + bowl_idx + 1e-5),
            # Severe penalty if one discipline fails minimum threshold
            np.minimum(bat_idx, bowl_idx) * 0.5
        ).round(2)

        ar_df["allrounder_composite_score"] = harmonic_score

        # Role designation refinement
        def classify_allrounder_archetype(row):
            if row["allrounder_composite_score"] >= 45.0 and row["discipline_balance_ratio"] >= 0.50:
                return "Genuine 2-Way All-Rounder"
            elif row["batting_impact_index"] > row["bowling_impact_index"] * 1.5:
                return "Batting All-Rounder (Bat Dominant)"
            elif row["bowling_impact_index"] > row["batting_impact_index"] * 1.5:
                return "Bowling All-Rounder (Pace/Spin Bowler with Bat)"
            else:
                return "Developing Dual-Discipline"

        ar_df["allrounder_archetype"] = ar_df.apply(classify_allrounder_archetype, axis=1)
        return ar_df

    def evaluate_wicketkeepers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluates wicketkeeper-batters combining batting performance with
        total dismissals, dismissals per match, and stumping ratio.
        """
        bat_df = self.batting_engine.calculate_batting_metrics(df)
        wk_df = bat_df.copy()

        # Total dismissals
        wk_df["total_dismissals"] = wk_df["catches"] + wk_df["stumpings"]
        
        # Dismissals per match
        wk_df["dismissals_per_match"] = np.where(
            wk_df["matches"] > 0,
            (wk_df["total_dismissals"] / wk_df["matches"]).round(2),
            0.0
        )

        # Stumping ratio: stumpings / max(1, total_dismissals)
        # Higher stumping ratio indicates superior standing-up keeping against spin bowling
        wk_df["stumping_ratio"] = np.where(
            wk_df["total_dismissals"] > 0,
            (wk_df["stumpings"] / wk_df["total_dismissals"]).round(3),
            0.0
        )

        # Keeping Impact Index (KII): scaled to 100 based on dismissals/match and stumpings
        # Baseline: 1.0 dismissal/match is solid, 1.5+ is elite
        dismissal_component = np.clip(wk_df["dismissals_per_match"] / 1.5, 0.0, 1.3) * 60.0
        stumping_component = np.clip(wk_df["stumping_ratio"] / 0.35, 0.0, 1.5) * 40.0
        wk_df["keeping_impact_index"] = (dismissal_component + stumping_component).round(2)

        # Composite Wicketkeeper Score (65% Batting Impact + 35% Glovework Impact)
        wk_df["wicketkeeper_composite_score"] = (
            (0.65 * wk_df["batting_impact_index"]) +
            (0.35 * wk_df["keeping_impact_index"])
        ).round(2)

        return wk_df

