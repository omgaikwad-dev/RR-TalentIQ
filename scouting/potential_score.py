"""
RR TalentIQ - Player Potential & Development Ceiling Engine
Models age curves, developmental headroom, and multi-year development ceilings
while keeping measured historical performance strictly separated from potential.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class PotentialScoreEngine:
    """
    Computes development ceiling and growth headroom for domestic talents.
    Young uncapped prospects (< 22) operating at high efficiency receive substantial
    future upside multipliers, reflecting their long-term auction return on investment.
    """

    @staticmethod
    def calculate_potential_score(
        age: Optional[float],
        measured_performance_index: float,
        sample_confidence: float = 1.0,
        discipline_efficiency: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculates developmental headroom and projected peak potential.
        
        Parameters:
        - age: Current decimal age relative to reference date
        - measured_performance_index: Empirical score (0-100)
        - sample_confidence: Confidence penalty factor (0-1)
        - discipline_efficiency: Underlying quality factor (e.g. boundary % or dot-ball suppression)
        
        Returns a dictionary with:
        - age_growth_multiplier: ceiling boost factor
        - developmental_headroom: potential points above current performance
        - projected_peak_potential: estimated ceiling rating (0-100)
        - potential_confidence: reliability of the potential estimate
        """
        if age is None or pd.isna(age):
            # Missing age receives neutral growth multiplier
            return {
                "age_growth_multiplier": 1.05,
                "developmental_headroom": 5.0,
                "projected_peak_potential": round(min(100.0, measured_performance_index * 1.05), 1),
                "potential_confidence": round(sample_confidence * 0.5, 2)
            }

        # Age Headroom Curve:
        # Age < 20.0: Extreme growth potential (+30% to +45% ceiling)
        # Age 20.0 - 22.0: High growth potential (+20% to +35%)
        # Age 22.1 - 24.5: Solid development window (+10% to +20%)
        # Age 24.6 - 27.0: Prime entering years (+5% to +10%)
        # Age > 27.0: Mature peak performance (+0% to +5%)
        if age < 20.0:
            base_growth = 1.40
        elif age < 22.0:
            base_growth = 1.30
        elif age < 24.5:
            base_growth = 1.18
        elif age < 27.0:
            base_growth = 1.08
        else:
            base_growth = 1.02

        # Efficiency bonus: younger players showing elite rate stats (SR, Econ) have higher conversion probability
        quality_adjustment = np.clip(discipline_efficiency, 0.85, 1.20)
        final_growth_multiplier = round(base_growth * quality_adjustment, 3)

        # Potential ceiling calculation bounded at 99.5
        unscaled_potential = measured_performance_index * final_growth_multiplier
        # Dampen potential if sample size is extremely small to prevent unrealistic hype
        potential_confidence = round(sample_confidence, 2)
        
        projected_potential = round(
            min(99.0, max(measured_performance_index, (unscaled_potential * 0.70 + measured_performance_index * 0.30) * (0.80 + 0.20 * sample_confidence))),
            1
        )
        headroom = round(max(0.0, projected_potential - measured_performance_index), 1)

        return {
            "age_growth_multiplier": final_growth_multiplier,
            "developmental_headroom": headroom,
            "projected_peak_potential": projected_potential,
            "potential_confidence": potential_confidence
        }

    @classmethod
    def enrich_dataset_with_potential(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates and attaches potential and development metrics to every player record.
        """
        p_df = df.copy()
        growth_multipliers = []
        headrooms = []
        projected_peaks = []
        confidences = []

        for _, row in p_df.iterrows():
            age = row.get("age", None)
            # Determine primary measured index based on role
            role = str(row.get("playing_role", ""))
            if "Bowler" in role:
                perf_idx = float(row.get("bowling_impact_index", row.get("economy", 50.0)) or 50.0)
                conf = float(row.get("sample_confidence_bowl", 0.7) or 0.7)
                eff = float(row.get("dot_ball_pct_bowl", 40.0) / 40.0)
            elif "All-Rounder" in role:
                perf_idx = float(row.get("allrounder_composite_score", 50.0) or 50.0)
                conf = float((row.get("sample_confidence_bat", 0.7) + row.get("sample_confidence_bowl", 0.7)) / 2.0)
                eff = 1.05
            elif "Wicketkeeper" in role:
                perf_idx = float(row.get("wicketkeeper_composite_score", row.get("batting_impact_index", 50.0)) or 50.0)
                conf = float(row.get("sample_confidence_bat", 0.7) or 0.7)
                eff = 1.0
            else:
                perf_idx = float(row.get("batting_impact_index", 50.0) or 50.0)
                conf = float(row.get("sample_confidence_bat", 0.7) or 0.7)
                eff = float(row.get("boundary_pct_bat", 60.0) / 60.0)

            res = cls.calculate_potential_score(age, perf_idx, conf, eff)
            growth_multipliers.append(res["age_growth_multiplier"])
            headrooms.append(res["developmental_headroom"])
            projected_peaks.append(res["projected_peak_potential"])
            confidences.append(res["potential_confidence"])

        p_df["age_growth_multiplier"] = growth_multipliers
        p_df["developmental_headroom"] = headrooms
        p_df["projected_peak_potential"] = projected_peaks
        p_df["potential_confidence"] = confidences
        return p_df

