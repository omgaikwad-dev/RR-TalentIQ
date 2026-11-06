"""
RR TalentIQ - Uncapped Talent Filtering Engine
Filters, partitions, and audits uncapped vs capped domestic players
with customizable age thresholds and role specifications.
"""

from typing import Optional, List
import pandas as pd
from scouting.age_eligibility import AgeEligibilityEngine, STATUS_CONFIRMED_UNCAPPED, STATUS_POTENTIALLY_UNCAPPED


def get_uncapped_player_pool(
    df: pd.DataFrame,
    max_age: Optional[float] = None,
    allow_potential: bool = True,
    roles: Optional[List[str]] = None,
    min_matches: int = 5
) -> pd.DataFrame:
    """
    Extracts the eligible uncapped domestic player pool meeting strict competition criteria.
    
    Parameters:
    - df: Standardized player dataframe
    - max_age: Maximum age threshold (e.g., 25.0 years)
    - allow_potential: Whether to include 'Potentially Uncapped' alongside 'Confirmed Uncapped'
    - roles: List of specific roles to filter by (or None for all)
    - min_matches: Minimum tournament match appearances for reliability
    """
    engine = AgeEligibilityEngine()
    audited_df = engine.audit_dataset_eligibility(df)
    
    # Filter 1: Capped status
    allowed_statuses = [STATUS_CONFIRMED_UNCAPPED]
    if allow_potential:
        allowed_statuses.append(STATUS_POTENTIALLY_UNCAPPED)
        
    filtered = audited_df[audited_df["uncapped_status"].isin(allowed_statuses)].copy()
    
    # Filter 2: Max age threshold
    if max_age is not None:
        filtered = filtered[(filtered["age"].notnull()) & (filtered["age"] <= max_age)]
        
    # Filter 3: Roles
    if roles:
        filtered = filtered[filtered["playing_role"].isin(roles)]
        
    # Filter 4: Sample size / match threshold
    if "matches" in filtered.columns:
        filtered = filtered[filtered["matches"] >= min_matches]
        
    return filtered.reset_index(drop=True)


def get_capped_exclusions_audit(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns all players excluded as Capped or International along with audit justification.
    """
    engine = AgeEligibilityEngine()
    audited_df = engine.audit_dataset_eligibility(df)
    excluded = audited_df[~audited_df["is_eligible_uncapped"]].copy()
    return excluded.reset_index(drop=True)

