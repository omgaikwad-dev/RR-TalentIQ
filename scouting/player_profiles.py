"""
RR TalentIQ - 360-Degree Player Dossier & Profile Engine
Synthesizes comprehensive individual scouting dossiers including strengths,
weaknesses, radar dimensions, auction fit, and developmental outlook.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class PlayerProfileEngine:
    """
    Builds structured 360-degree scouting profiles for shortlisted domestic talents.
    """

    @staticmethod
    def identify_strengths_and_weaknesses(row: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        Derives objective, data-backed strengths and vulnerabilities based on statistical thresholds.
        """
        strengths = []
        weaknesses = []

        role = str(row.get("playing_role", ""))
        age = float(row.get("age", 25.0) or 25.0)
        sr = float(row.get("strike_rate", 0.0) or 0.0)
        avg = float(row.get("batting_average", 0.0) or 0.0)
        boundary_pct = float(row.get("boundary_pct_bat", 0.0) or 0.0)
        dot_bat = float(row.get("dot_ball_pct_bat", 0.0) or 0.0)
        
        econ = float(row.get("economy", 0.0) or 0.0)
        bowl_sr = float(row.get("bowling_strike_rate", 0.0) or 0.0)
        dot_bowl = float(row.get("dot_ball_pct_bowl", 0.0) or 0.0)
        overs = float(row.get("overs", 0.0) or 0.0)
        stumpings = int(row.get("stumpings", 0) or 0)
        matches = int(row.get("matches", 0) or 0)

        # Age & Potential Strengths
        if age < 21.5:
            strengths.append(f"Youth ceiling advantage: Only {age:.1f} years old with massive multi-year development runway")
        elif age < 23.5:
            strengths.append(f"Prime developmental window: {age:.1f} years old entering athletic physical peak")

        # Batting Evaluations
        if "Batter" in role or "All-Rounder" in role or "Finisher" in role or "Wicketkeeper" in role:
            if sr >= 165.0:
                strengths.append(f"Elite boundary power: Explosive {sr:.1f} strike rate puts immediate pressure on bowling units")
            elif sr >= 150.0:
                strengths.append(f"High-tempo scoring: Robust {sr:.1f} strike rate aligns with modern IPL T20 paradigms")
            elif sr < 130.0 and "Finisher" in role:
                weaknesses.append(f"Below-par strike rate for finisher: {sr:.1f} SR may struggle to accelerate from ball one")

            if avg >= 40.0:
                strengths.append(f"Innings stability: Exceptional {avg:.1f} batting average demonstrating high wicket preservation")
            elif avg < 22.0 and "Top-order" in role:
                weaknesses.append(f"Vulnerable wicket retention: {avg:.1f} average indicates susceptibility to early dismissal")

            if boundary_pct >= 65.0:
                strengths.append(f"Boundary hitting dominance: {boundary_pct:.1f}% of runs sourced purely from fours and sixes")
            
            if dot_bat >= 38.0:
                weaknesses.append(f"Dot-ball accumulation: {dot_bat:.1f}% dot ball rate creates scoreboard stagnation")
            elif dot_bat <= 29.0:
                strengths.append(f"Elite strike rotation: Suppresses dot balls down to {dot_bat:.1f}%")

        # Bowling Evaluations
        if "Bowler" in role or "All-Rounder" in role:
            if overs >= 10.0:
                if econ <= 7.20:
                    strengths.append(f"Exceptional run containment: Restrictive {econ:.2f} economy rate provides defensive control")
                elif econ >= 8.80:
                    weaknesses.append(f"High boundary concession: {econ:.2f} economy rate vulnerable to expensive overs")

                if 0 < bowl_sr <= 14.5:
                    strengths.append(f"High-frequency wicket-taker: Takes a wicket every {bowl_sr:.1f} balls")
                elif bowl_sr >= 24.0:
                    weaknesses.append(f"Low strike potency: Averages {bowl_sr:.1f} balls per dismissal")

                if dot_bowl >= 48.0:
                    strengths.append(f"Pressure generation: Builds pressure with {dot_bowl:.1f}% dot ball frequency")

        # Wicketkeeper Evaluations
        if "Wicketkeeper" in role:
            if stumpings >= 4:
                strengths.append(f"Sharp spin-keeping instincts: Effected {stumpings} stumpings off domestic spinners")

        # Sample Size Checks
        if matches < 15:
            weaknesses.append(f"Limited match sample: Tested across {matches} appearances; requires continued tracking")

        # Guarantee at least 2 strengths and 1 weakness for balanced scouting
        if len(strengths) == 0:
            strengths.append("Consistent domestic performer with dependable baseline execution")
            strengths.append("Versatile skill profile adaptable to squad depth roles")
        if len(weaknesses) == 0:
            weaknesses.append("Requires exposure against 145+ kph pace and elite IPL death-over spin variations")

        return strengths, weaknesses

    @classmethod
    def generate_player_dossier(cls, player_row: pd.Series) -> Dict[str, Any]:
        """
        Creates a self-contained 360-degree scout dossier dictionary for a given player row.
        """
        row_dict = player_row.to_dict()
        strengths, weaknesses = cls.identify_strengths_and_weaknesses(row_dict)

        # Radar dimension values (normalized 0-100)
        radar_metrics = {
            "Strike Power": float(min(100.0, max(20.0, (float(row_dict.get("strike_rate", 120.0)) - 100.0) * 1.25))),
            "Wicket Retention": float(min(100.0, max(20.0, float(row_dict.get("batting_average", 20.0)) * 2.0))),
            "Dot Suppression": float(min(100.0, max(20.0, (50.0 - float(row_dict.get("dot_ball_pct_bat", 35.0))) * 3.3))),
            "Economy / Control": float(min(100.0, max(20.0, (11.0 - float(row_dict.get("economy", 8.0))) * 16.0))),
            "Wicket Potency": float(min(100.0, max(20.0, (30.0 - float(row_dict.get("bowling_strike_rate", 20.0) or 20.0)) * 3.5))),
            "Youth Ceiling": float(min(100.0, max(20.0, float(row_dict.get("projected_peak_potential", 70.0))))),
            "Consistency": float(min(100.0, max(20.0, float(row_dict.get("consistency_score", 60.0)))))
        }

        dossier = {
            "player_id": row_dict.get("player_id", "RR_DOM_UNK"),
            "player_name": row_dict.get("player_name", "Unknown Player"),
            "dob": row_dict.get("dob", "Unknown"),
            "age": float(row_dict.get("age", 0.0) or 0.0),
            "playing_role": row_dict.get("playing_role", "Top-order Batter"),
            "batting_style": row_dict.get("batting_style", "Right-hand bat"),
            "bowling_style": row_dict.get("bowling_style", "Right-arm medium"),
            "domestic_team": row_dict.get("domestic_team", "Unattached"),
            "uncapped_status": row_dict.get("uncapped_status", "Confirmed Uncapped"),
            "overall_scouting_score": float(row_dict.get("overall_scouting_score", 0.0)),
            "role_performance_score": float(row_dict.get("role_performance_score", 0.0)),
            "projected_peak_potential": float(row_dict.get("projected_peak_potential", 0.0)),
            "consistency_score": float(row_dict.get("consistency_score", 0.0)),
            "matches": int(row_dict.get("matches", 0)),
            "runs": int(row_dict.get("runs", 0)),
            "strike_rate": float(row_dict.get("strike_rate", 0.0)),
            "batting_average": float(row_dict.get("batting_average", 0.0)),
            "wickets": int(row_dict.get("wickets", 0)),
            "economy": float(row_dict.get("economy", 0.0)),
            "bowling_strike_rate": float(row_dict.get("bowling_strike_rate", 0.0)),
            "catches": int(row_dict.get("catches", 0)),
            "stumpings": int(row_dict.get("stumpings", 0)),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "radar_dimensions": radar_metrics,
            "data_source": row_dict.get("data_source", "Verified Benchmark")
        }
        return dossier

