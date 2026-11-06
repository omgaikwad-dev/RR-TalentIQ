"""
RR TalentIQ - Rajasthan Royals Squad Requirements & Priority Matrix
Translates structural roster gaps into actionable, weighted scouting objectives
and ideal statistical profile benchmarks for the IPL 2027 auction.
"""

from typing import Dict, Any, List
import pandas as pd


# RR Priority Tactical Gaps for IPL 2027
SCOUTING_PRIORITY_TARGETS = [
    {
        "priority_rank": 1,
        "target_need": "Young Indian Outswing Powerplay Pacer",
        "rationale": "Eventual successor to Trent Boult. Must possess genuine swing and control at 138–142 kph to exploit Sawai Mansingh Stadium pitch conditions.",
        "target_role": "Pace Bowler",
        "benchmark_metrics": "Economy <= 7.60, Bowling SR <= 15.0, Dot % >= 48%",
        "ideal_age_bracket": "< 23.0 years",
        "recommended_shortlist": ["Raj Limbani", "Vaibhav Arora"]
    },
    {
        "priority_rank": 2,
        "target_need": "Middle-Overs Spin Enforcer / Mystery Wrist Spinner",
        "rationale": "Strategic spin succession plan for Ravichandran Ashwin and Yuzvendra Chahal. Requires tight trajectory and deceptive variations.",
        "target_role": "Spin Bowler",
        "benchmark_metrics": "Economy <= 7.20, Bowling SR <= 16.0, Dot % >= 50%",
        "ideal_age_bracket": "< 24.0 years",
        "recommended_shortlist": ["Saumy Pandey", "Digvesh Rathi", "Manav Suthar"]
    },
    {
        "priority_rank": 3,
        "target_need": "Dual-Discipline Lower-Order All-Rounder",
        "rationale": "Solves RR's classic 'tail-too-long' problem. Needs a player who can strike at 145+ at No. 7/8 and deliver 3–4 competitive overs.",
        "target_role": "Bowling All-Rounder / Batting All-Rounder",
        "benchmark_metrics": "Strike Rate >= 140.0, Bat Avg >= 22.0, Economy <= 7.80, Wickets >= 1.0/game",
        "ideal_age_bracket": "< 24.0 years",
        "recommended_shortlist": ["Musheer Khan", "Vipraj Nigam"]
    },
    {
        "priority_rank": 4,
        "target_need": "Explosive Middle-Order / Spin Destroyer",
        "rationale": "Takes pressure off Shimron Hetmyer and Sanju Samson in overs 11–17. Must feature exceptional boundary hitting against domestic spinners.",
        "target_role": "Finisher / Middle-order Batter",
        "benchmark_metrics": "Strike Rate >= 160.0, Boundary % >= 65%, Dot % <= 30%",
        "ideal_age_bracket": "< 25.0 years",
        "recommended_shortlist": ["Sameer Rizvi", "Ashutosh Sharma"]
    },
    {
        "priority_rank": 5,
        "target_need": "Dynamic Left-Handed Powerplay Opener",
        "rationale": "Insurance and developmental successor for Yashasvi Jaiswal. Allows RR to maintain fearless opening velocity even if rotations occur.",
        "target_role": "Top-order Batter",
        "benchmark_metrics": "Powerplay SR >= 155.0, 50s Conversion >= 20%",
        "ideal_age_bracket": "< 22.0 years",
        "recommended_shortlist": ["Priyansh Arya", "Ayush Mhatre"]
    }
]


class SquadRequirementsEngine:
    """
    Translates tactical squad needs into scouting target priorities and suitability filters.
    """

    @staticmethod
    def get_priority_matrix() -> pd.DataFrame:
        """Returns the ranked matrix of tactical squad requirements."""
        return pd.DataFrame(SCOUTING_PRIORITY_TARGETS)

    @classmethod
    def calculate_squad_fit_score(cls, player_row: Dict[str, Any]) -> float:
        """
        Computes a squad suitability score (0-100) based on how directly the player
        addresses RR's top 5 priority roster gaps.
        """
        role = str(player_row.get("playing_role", ""))
        age = float(player_row.get("age", 25.0) or 25.0)
        sr = float(player_row.get("strike_rate", 120.0) or 120.0)
        econ = float(player_row.get("economy", 8.5) or 8.5)
        bowl_sr = float(player_row.get("bowling_strike_rate", 24.0) or 24.0)
        p_name = str(player_row.get("player_name", ""))

        fit_score = 60.0  # Base fit for any verified domestic talent

        # Priority 1: Young Pacer (< 23, Econ < 8.0, Bowl SR < 16)
        if "Pace Bowler" in role:
            if age < 23.0 and econ <= 7.8 and bowl_sr <= 16.0:
                fit_score += 35.0
            elif age < 25.0 and econ <= 8.2:
                fit_score += 20.0

        # Priority 2: Young Spinner (< 24, Econ < 7.3)
        elif "Spin Bowler" in role:
            if age < 24.0 and econ <= 7.2:
                fit_score += 35.0
            elif econ <= 7.6:
                fit_score += 20.0

        # Priority 3: All-Rounder (Genuine 2-way)
        elif "All-Rounder" in role:
            ar_score = float(player_row.get("allrounder_composite_score", 0.0) or 0.0)
            if ar_score >= 35.0 and age < 25.0:
                fit_score += 35.0
            elif ar_score >= 20.0:
                fit_score += 20.0

        # Priority 4: Finisher (SR >= 160)
        elif "Finisher" in role:
            if sr >= 165.0:
                fit_score += 35.0
            elif sr >= 150.0:
                fit_score += 20.0

        # Priority 5: Top-order Opener (SR >= 155, Age < 22)
        elif "Top-order" in role:
            if age < 22.0 and sr >= 150.0:
                fit_score += 30.0
            elif sr >= 160.0:
                fit_score += 25.0

        return round(min(99.0, fit_score), 1)

