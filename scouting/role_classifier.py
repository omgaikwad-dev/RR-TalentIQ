"""
RR TalentIQ - Role Classification Engine
Classifies and verifies cricket playing roles and specialized archetypes
based on empirical batting, bowling, and wicketkeeping involvement.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


# Standardized Playing Roles
ROLE_TOP_ORDER = "Top-order Batter"
ROLE_MIDDLE_ORDER = "Middle-order Batter"
ROLE_FINISHER = "Finisher"
ROLE_WICKETKEEPER = "Wicketkeeper-Batter"
ROLE_BATTING_ALLROUNDER = "Batting All-Rounder"
ROLE_BOWLING_ALLROUNDER = "Bowling All-Rounder"
ROLE_PACE_BOWLER = "Pace Bowler"
ROLE_SPIN_BOWLER = "Spin Bowler"

ALL_ROLES = [
    ROLE_TOP_ORDER,
    ROLE_MIDDLE_ORDER,
    ROLE_FINISHER,
    ROLE_WICKETKEEPER,
    ROLE_BATTING_ALLROUNDER,
    ROLE_BOWLING_ALLROUNDER,
    ROLE_PACE_BOWLER,
    ROLE_SPIN_BOWLER
]


class RoleClassifier:
    """
    Infers and audits player roles from actual match performance data
    to prevent misclassification (e.g., mislabeling a keeper as a pure batter).
    """

    @staticmethod
    def infer_role(row: Dict[str, Any]) -> str:
        """
        Infers the most accurate playing role based on statistics.
        """
        declared_role = str(row.get("playing_role", "")).strip()
        stumpings = int(row.get("stumpings", 0) or 0)
        catches = int(row.get("catches", 0) or 0)
        overs = float(row.get("overs", 0.0) or 0.0)
        balls_faced = int(row.get("balls_faced", 0) or 0)
        runs = int(row.get("runs", 0) or 0)
        strike_rate = float(row.get("strike_rate", 0.0) or 0.0)
        bowl_style = str(row.get("bowling_style", "")).lower()

        # 1. Wicketkeeper check: Any stumpings or designated keeper
        if stumpings >= 1 or "wicketkeeper" in declared_role.lower() or "keeper" in declared_role.lower():
            return ROLE_WICKETKEEPER

        # 2. Genuine Dual-Threat All-Rounders
        if balls_faced >= 80 and overs >= 15.0:
            if runs > (overs * 15):
                return ROLE_BATTING_ALLROUNDER
            else:
                return ROLE_BOWLING_ALLROUNDER

        # 3. Specialist Bowlers (Minimal batting, substantial bowling)
        if overs >= 12.0 and balls_faced < 100:
            if any(term in bowl_style for term in ["spin", "orthodox", "legbreak", "offbreak", "slow"]):
                return ROLE_SPIN_BOWLER
            else:
                return ROLE_PACE_BOWLER

        # 4. Batting Archetypes
        if balls_faced >= 80 or runs >= 120:
            # High SR, lower balls per match indicates Finisher
            if strike_rate >= 160.0:
                return ROLE_FINISHER
            elif declared_role in [ROLE_TOP_ORDER, ROLE_MIDDLE_ORDER]:
                return declared_role
            else:
                return ROLE_TOP_ORDER if strike_rate < 145.0 else ROLE_MIDDLE_ORDER

        # Default fallback to declared role if recognized, else Top-order Batter
        return declared_role if declared_role in ALL_ROLES else ROLE_TOP_ORDER

    @classmethod
    def audit_and_apply_roles(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validates roles across the dataset and updates the 'playing_role' column.
        """
        r_df = df.copy()
        inferred_roles = []
        for _, row in r_df.iterrows():
            inferred_roles.append(cls.infer_role(row))
        r_df["inferred_role"] = inferred_roles
        # Preserve declared role if already valid, otherwise apply inferred
        r_df["playing_role"] = np.where(
            r_df["playing_role"].isin(ALL_ROLES),
            r_df["playing_role"],
            r_df["inferred_role"]
        )
        return r_df

