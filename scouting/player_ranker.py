"""
RR TalentIQ - Player Ranking & Multi-Criteria Decision Engine
Computes transparent role-specific ratings, overall scouting scores,
and conducts sensitivity analysis across varying weight paradigms.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from analytics.batting_scouting import BattingScoutingEngine
from analytics.bowling_scouting import BowlingScoutingEngine
from analytics.allrounder_scouting import DualDisciplineScoutingEngine
from analytics.consistency_analysis import ConsistencyAnalyzer
from analytics.performance_normalization import PerformanceNormalizer
from scouting.role_classifier import (
    RoleClassifier,
    ROLE_TOP_ORDER,
    ROLE_MIDDLE_ORDER,
    ROLE_FINISHER,
    ROLE_WICKETKEEPER,
    ROLE_BATTING_ALLROUNDER,
    ROLE_BOWLING_ALLROUNDER,
    ROLE_PACE_BOWLER,
    ROLE_SPIN_BOWLER
)
from scouting.potential_score import PotentialScoreEngine


# Default Recommended Multi-Criteria Scouting Weights
DEFAULT_WEIGHTS = {
    "role_performance": 0.45,
    "development_potential": 0.25,
    "consistency": 0.15,
    "sample_confidence": 0.15
}


class PlayerRanker:
    """
    Ranks players objectively using role-calibrated multi-criteria decision modeling.
    Provides full transparency, auditability, and sensitivity analysis.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        # Ensure weights sum to 1.0
        total_w = sum(self.weights.values())
        if abs(total_w - 1.0) > 1e-4:
            self.weights = {k: v / total_w for k, v in self.weights.items()}

        self.bat_engine = BattingScoutingEngine()
        self.bowl_engine = BowlingScoutingEngine()
        self.dual_engine = DualDisciplineScoutingEngine()

    def rank_players(
        self,
        df: pd.DataFrame,
        weights: Optional[Dict[str, float]] = None,
        role_filter: Optional[str] = None,
        max_age: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Executes end-to-end player scoring and returns a sorted leaderboard.
        """
        w = weights or self.weights
        total_w = sum(w.values())
        norm_weights = {k: v / total_w for k, v in w.items()}

        # 1. Ensure Role Classification
        r_df = RoleClassifier.audit_and_apply_roles(df)

        # 2. Enrich with Batting, Bowling, and Dual Metrics
        bat_df = self.bat_engine.calculate_batting_metrics(r_df)
        bowl_df = self.bowl_engine.calculate_bowling_metrics(bat_df)
        dual_df = self.dual_engine.evaluate_allrounders(bowl_df)
        wk_df = self.dual_engine.evaluate_wicketkeepers(dual_df)

        # 3. Add Consistency & Sample Reliability
        c_df = ConsistencyAnalyzer.calculate_consistency_score(wk_df)

        # 4. Add Potential Ceiling Metrics
        p_df = PotentialScoreEngine.enrich_dataset_with_potential(c_df)

        # 5. Normalize Core Feature Columns
        scored_df = PerformanceNormalizer.normalize_scouting_metrics(p_df)

        # 6. Compute Role-Specific Discipline Scores
        # Batting Score (0-100)
        scored_df["batting_score"] = (
            (0.40 * scored_df.get("norm_strike_rate", 50.0)) +
            (0.30 * scored_df.get("norm_batting_avg", 50.0)) +
            (0.20 * scored_df.get("norm_boundary_pct", 50.0)) +
            (0.10 * scored_df.get("norm_bat_dot_suppression", 50.0))
        ).round(1)

        # Bowling Score (0-100)
        scored_df["bowling_score"] = (
            (0.40 * scored_df.get("norm_economy", 50.0)) +
            (0.35 * scored_df.get("norm_bowling_sr", 50.0)) +
            (0.15 * scored_df.get("norm_bowl_dots", 50.0)) +
            (0.10 * scored_df.get("norm_wickets", 50.0))
        ).round(1)

        # All-Rounder Score (0-100)
        bat_s = scored_df["batting_score"]
        bowl_s = scored_df["bowling_score"]
        harmonic_s = (2.0 * bat_s * bowl_s) / (bat_s + bowl_s + 1e-5)
        scored_df["allrounder_score"] = (harmonic_s * scored_df["discipline_balance_ratio"]).round(1)

        # Wicketkeeper Score (0-100)
        scored_df["wicketkeeper_score"] = (
            (0.65 * scored_df["batting_score"]) +
            (0.35 * scored_df.get("keeping_impact_index", 50.0))
        ).round(1)

        # 7. Map Primary Role Performance Metric
        def get_role_perf_score(row):
            role = row["playing_role"]
            if role in [ROLE_TOP_ORDER, ROLE_MIDDLE_ORDER, ROLE_FINISHER]:
                return row["batting_score"]
            elif role in [ROLE_PACE_BOWLER, ROLE_SPIN_BOWLER]:
                return row["bowling_score"]
            elif role in [ROLE_BATTING_ALLROUNDER, ROLE_BOWLING_ALLROUNDER]:
                return row["allrounder_score"]
            elif role == ROLE_WICKETKEEPER:
                return row["wicketkeeper_score"]
            else:
                return row["batting_score"]

        scored_df["role_performance_score"] = scored_df.apply(get_role_perf_score, axis=1)

        # 8. Compute Overall Scouting Score (OSS)
        # OSS = w_perf * role_perf + w_pot * potential + w_cons * consistency + w_conf * sample_confidence
        # Note: sample_confidence factor scaled from 0-1 to 0-100
        conf_factor = np.where(
            scored_df["playing_role"].str.contains("Bowler"),
            scored_df.get("sample_confidence_bowl", 0.7),
            scored_df.get("sample_confidence_bat", 0.7)
        ) * 100.0

        scored_df["overall_scouting_score"] = (
            (norm_weights["role_performance"] * scored_df["role_performance_score"]) +
            (norm_weights["development_potential"] * scored_df["projected_peak_potential"]) +
            (norm_weights["consistency"] * scored_df["consistency_score"]) +
            (norm_weights["sample_confidence"] * conf_factor)
        ).round(1)

        # Apply optional filters
        filtered = scored_df.copy()
        if role_filter and role_filter != "All":
            filtered = filtered[filtered["playing_role"] == role_filter]
        if max_age is not None:
            filtered = filtered[(filtered["age"].notnull()) & (filtered["age"] <= max_age)]

        # Sort descending by Overall Scouting Score
        ranked = filtered.sort_values(by=["overall_scouting_score", "role_performance_score"], ascending=False).reset_index(drop=True)
        ranked.index = ranked.index + 1
        ranked["rank"] = ranked.index
        return ranked

    def run_sensitivity_analysis(
        self,
        df: pd.DataFrame,
        weight_profiles: Optional[Dict[str, Dict[str, float]]] = None
    ) -> pd.DataFrame:
        """
        Runs sensitivity analysis across three distinct strategic paradigms:
        1. Baseline (Balanced): 45% Perf, 25% Potential, 15% Consistency, 15% Sample Conf
        2. Youth & Ceiling Dominant: 30% Perf, 45% Potential, 15% Consistency, 10% Sample Conf
        3. Immediate Ready Impact: 60% Perf, 10% Potential, 20% Consistency, 10% Sample Conf
        
        Returns comparative ranks and rank variance for each player.
        """
        if weight_profiles is None:
            weight_profiles = {
                "Balanced (Recommended)": {
                    "role_performance": 0.45, "development_potential": 0.25,
                    "consistency": 0.15, "sample_confidence": 0.15
                },
                "High Potential (Youth Ceilings)": {
                    "role_performance": 0.30, "development_potential": 0.45,
                    "consistency": 0.15, "sample_confidence": 0.10
                },
                "Win-Now (Immediate Impact)": {
                    "role_performance": 0.60, "development_potential": 0.10,
                    "consistency": 0.20, "sample_confidence": 0.10
                }
            }

        comparison_records = {}
        for profile_name, weights in weight_profiles.items():
            ranked_res = self.rank_players(df, weights=weights)
            for r, row in ranked_res.iterrows():
                p_name = row["player_name"]
                if p_name not in comparison_records:
                    comparison_records[p_name] = {
                        "player_name": p_name,
                        "age": row.get("age", None),
                        "playing_role": row["playing_role"],
                        "uncapped_status": row.get("uncapped_status", "Confirmed Uncapped")
                    }
                comparison_records[p_name][f"rank_{profile_name}"] = int(r)
                comparison_records[p_name][f"score_{profile_name}"] = float(row["overall_scouting_score"])

        sens_df = pd.DataFrame(list(comparison_records.values()))
        rank_cols = [c for c in sens_df.columns if c.startswith("rank_")]
        sens_df["rank_range"] = sens_df[rank_cols].max(axis=1) - sens_df[rank_cols].min(axis=1)
        sens_df["rank_stability"] = np.where(sens_df["rank_range"] <= 2, "Ultra Stable", np.where(sens_df["rank_range"] <= 4, "Moderately Stable", "Sensitive to Weights"))
        
        # Sort by primary balanced rank
        primary_col = [c for c in rank_cols if "Balanced" in c][0]
        sens_df = sens_df.sort_values(by=primary_col).reset_index(drop=True)
        sens_df.index = sens_df.index + 1
        return sens_df

