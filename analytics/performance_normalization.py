"""
RR TalentIQ - Performance Normalization & Standardized Indexing
Scales raw cricket performance metrics across tournaments using min-max
and percentile normalization to create uniform [0, 100] statistical ratings.
"""

from typing import List, Optional, Dict
import pandas as pd
import numpy as np


class PerformanceNormalizer:
    """
    Standardizes performance metrics onto normalized 0-100 scales
    for objective role-based multi-criteria evaluation.
    """

    @staticmethod
    def min_max_scale(series: pd.Series, invert: bool = False) -> pd.Series:
        """
        Scales a numeric series to 0–100.
        If invert=True, lower original values yield higher scores (e.g. economy, bowling average).
        """
        s = pd.to_numeric(series, errors="coerce").fillna(0.0)
        s_min = s.min()
        s_max = s.max()
        
        if s_max == s_min:
            return pd.Series(50.0, index=series.index)
            
        scaled = ((s - s_min) / (s_max - s_min)) * 100.0
        if invert:
            scaled = 100.0 - scaled
        return scaled.round(1)

    @staticmethod
    def percentile_rank(series: pd.Series, invert: bool = False) -> pd.Series:
        """Computes empirical percentile ranking (0–100) within the pool."""
        s = pd.to_numeric(series, errors="coerce").fillna(0.0)
        pct = (s.rank(pct=True, ascending=not invert) * 100.0).round(1)
        return pct

    @classmethod
    def normalize_scouting_metrics(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates normalized [0-100] percentile scores for all core metrics.
        """
        n_df = df.copy()

        # Batting normalizations (higher is better)
        if "strike_rate" in n_df.columns:
            n_df["norm_strike_rate"] = cls.min_max_scale(n_df["strike_rate"])
        if "batting_average" in n_df.columns:
            n_df["norm_batting_avg"] = cls.min_max_scale(n_df["batting_average"])
        if "boundary_pct_bat" in n_df.columns:
            n_df["norm_boundary_pct"] = cls.min_max_scale(n_df["boundary_pct_bat"])
        if "dot_ball_pct_bat" in n_df.columns:
            # In batting, lower dot-ball % is better
            n_df["norm_bat_dot_suppression"] = cls.min_max_scale(n_df["dot_ball_pct_bat"], invert=True)

        # Bowling normalizations
        if "economy" in n_df.columns:
            # Lower economy is better
            n_df["norm_economy"] = cls.min_max_scale(n_df["economy"], invert=True)
        if "bowling_strike_rate" in n_df.columns:
            # Filter zeros before inverting
            valid_bowl_sr = np.where(n_df["bowling_strike_rate"] > 0, n_df["bowling_strike_rate"], 40.0)
            n_df["norm_bowling_sr"] = cls.min_max_scale(pd.Series(valid_bowl_sr), invert=True)
        if "wickets" in n_df.columns:
            n_df["norm_wickets"] = cls.min_max_scale(n_df["wickets"])
        if "dot_ball_pct_bowl" in n_df.columns:
            # In bowling, higher dot-ball % is better
            n_df["norm_bowl_dots"] = cls.min_max_scale(n_df["dot_ball_pct_bowl"])

        return n_df

