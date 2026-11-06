"""
RR TalentIQ - Model Explainability & Feature Attribution Engine
Breaks down feature deviations, cluster proximity, positive/negative drivers,
and data coverage confidence to make ML findings human-interpretable.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class MLExplainabilityEngine:
    """
    Transparent explainability engine that answers:
    'Why does this player belong to this statistical cluster or tier?'
    """

    @staticmethod
    def explain_player_features(
        player_name: str,
        df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Computes z-score deviations of an individual player relative to the domestic cohort
        to identify their defining performance drivers.
        """
        match = df[df["player_name"] == player_name]
        if len(match) == 0:
            return {"error": f"Player {player_name} not found in dataset."}

        p_row = match.iloc[0]
        cols = feature_cols or [
            "strike_rate", "batting_average", "boundary_pct_bat", "dot_ball_pct_bat",
            "economy", "bowling_strike_rate", "wickets", "runs", "age"
        ]
        available_cols = [c for c in cols if c in df.columns]

        positive_drivers = []
        negative_drivers = []
        feature_details = {}

        for col in available_cols:
            val = float(p_row.get(col, 0.0) or 0.0)
            pop_mean = float(df[col].mean())
            pop_std = float(df[col].std()) if df[col].std() > 0 else 1.0

            z_score = round((val - pop_mean) / pop_std, 2)
            
            # Format feature label
            clean_label = col.replace("_", " ").title()

            # Note: For economy, dot_ball_pct_bat, lower is better
            invert = col in ["economy", "dot_ball_pct_bat"]
            effective_z = -z_score if invert else z_score

            feature_details[clean_label] = {
                "player_value": round(val, 2),
                "cohort_average": round(pop_mean, 2),
                "z_score": z_score,
                "is_positive": effective_z > 0.0
            }

            if effective_z >= 0.75:
                direction = "superior" if not invert else "restrictive (low)"
                positive_drivers.append(f"{clean_label}: {val} ({direction}, +{effective_z:.1f}σ vs cohort)")
            elif effective_z <= -0.75:
                direction = "lagging" if not invert else "elevated (high)"
                negative_drivers.append(f"{clean_label}: {val} ({direction}, {effective_z:.1f}σ vs cohort)")

        # Data coverage score (percentage of core metrics available without imputation)
        non_null_count = sum(1 for c in available_cols if pd.notnull(p_row.get(c)))
        data_coverage_pct = round((non_null_count / len(available_cols)) * 100, 1)

        return {
            "player_name": player_name,
            "playing_role": p_row.get("playing_role", "Domestic Player"),
            "cluster_archetype": p_row.get("cluster_archetype", "Unclustered"),
            "overall_scouting_score": float(p_row.get("overall_scouting_score", 0.0)),
            "data_coverage_pct": data_coverage_pct,
            "positive_drivers": positive_drivers if positive_drivers else ["Balanced cohort-level execution across evaluated metrics"],
            "negative_drivers": negative_drivers if negative_drivers else ["No statistical vulnerabilities > 0.75σ below cohort mean"],
            "feature_breakdown": feature_details
        }

