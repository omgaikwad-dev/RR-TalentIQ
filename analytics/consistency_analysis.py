"""
RR TalentIQ - Consistency & Reliability Analytics Module
Calculates performance volatility, innings milestone conversion rates,
sample-size reliability weights, and recent form momentum.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class ConsistencyAnalyzer:
    """
    Computes mathematical consistency scores, milestone conversion rates,
    and sample-size confidence discount factors.
    """

    @staticmethod
    def calculate_consistency_score(df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches player records with consistency indices.
        Formula incorporates:
        1. Fifty-conversion rate: 50s / max(1, innings_batted)
        2. Average runs per dismissal stability
        3. Match participation continuity
        4. Economy stability (for bowlers)
        """
        c_df = df.copy()

        # Fifty conversion rate (percentage of innings with 50+ score)
        innings = np.maximum(1, c_df.get("innings_batted", c_df.get("matches", 1)))
        fifties = c_df.get("fifties", 0)
        c_df["fifty_conversion_rate"] = ((fifties / innings) * 100).round(2)

        # Batting stability: reward high average with high strike rate
        bat_avg = c_df.get("batting_average", 0)
        # Ratio of average to standard deviation estimate
        # In T20, an average above 35.0 with SR > 140 indicates world-class consistency
        bat_consistency_component = np.clip((bat_avg / 35.0) * 50.0, 0.0, 60.0)
        
        # Bowling stability: reward lower economy and lower bowling average
        bowl_avg = c_df.get("bowling_average", 0)
        econ = c_df.get("economy", 8.0)
        
        # Bowler consistency: reward economy < 7.5 and average < 22
        bowl_consistency_component = np.where(
            c_df.get("overs", 0) > 5.0,
            np.clip((9.0 - econ) * 10.0 + (28.0 - bowl_avg) * 1.5, 0.0, 40.0),
            0.0
        )

        # Baseline participation continuity factor (matches / 15)
        matches = c_df.get("matches", 1)
        participation_factor = np.clip(matches / 15.0, 0.4, 1.0)

        # Composite consistency score out of 100
        raw_consistency = (bat_consistency_component + bowl_consistency_component + (c_df["fifty_conversion_rate"] * 0.4))
        c_df["consistency_score"] = (np.clip(raw_consistency, 10.0, 95.0) * participation_factor).round(1)

        # Sample Size Reliability Category
        def classify_sample_size(row):
            m = row.get("matches", 0)
            bf = row.get("balls_faced", 0)
            ov = row.get("overs", 0)
            if m >= 25 or bf >= 400 or ov >= 70:
                return "Robust Sample (High Confidence)"
            elif m >= 12 or bf >= 150 or ov >= 25:
                return "Adequate Sample (Moderate Confidence)"
            else:
                return "Small Sample (High Uncertainty)"

        c_df["sample_reliability_category"] = c_df.apply(classify_sample_size, axis=1)
        return c_df

