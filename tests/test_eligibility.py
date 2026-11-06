"""
RR TalentIQ - Unit Tests for Age & Eligibility Engine
Tests age calculation, uncapped evaluation, capped player exclusion, and DOB audits.
"""

import pytest
import pandas as pd
from scouting.age_eligibility import (
    AgeEligibilityEngine,
    STATUS_CONFIRMED_UNCAPPED,
    STATUS_CAPPED,
    DEFAULT_AGE_REFERENCE_DATE
)
from scouting.uncapped_filter import get_uncapped_player_pool, get_capped_exclusions_audit


@pytest.fixture
def eligibility_engine():
    return AgeEligibilityEngine(reference_date=DEFAULT_AGE_REFERENCE_DATE)


def test_exact_age_calculation(eligibility_engine):
    """Verifies decimal age calculation relative to the reference date 2027-01-01."""
    # Born 2005-01-01 -> Exactly 22.01 years on 2027-01-01
    age, note = eligibility_engine.calculate_exact_age("2005-01-01")
    assert age is not None
    assert round(age, 1) == 22.0
    assert note == "Verified DOB"

    # Future date -> Should flag invalid
    age_future, note_future = eligibility_engine.calculate_exact_age("2028-05-10")
    assert age_future is None
    assert "Future" in note_future


def test_capped_player_flagging(eligibility_engine):
    """Verifies that known capped Indian players (e.g. Virat Kohli, Jasprit Bumrah) are flagged Capped."""
    res_kohli = eligibility_engine.evaluate_player_eligibility("Virat Kohli", "1988-11-05")
    assert res_kohli["uncapped_status"] == STATUS_CAPPED
    assert res_kohli["is_eligible_uncapped"] is False

    res_bumrah = eligibility_engine.evaluate_player_eligibility("Jasprit Bumrah", "1993-12-06")
    assert res_bumrah["uncapped_status"] == STATUS_CAPPED
    assert res_bumrah["is_eligible_uncapped"] is False


def test_uncapped_youth_classification(eligibility_engine):
    """Verifies that an uncapped teenager is categorized as 'Under 21 (Elite Youth)'."""
    res = eligibility_engine.evaluate_player_eligibility(
        player_name="Young Prodigy",
        dob_val="2006-08-15",
        provided_status=STATUS_CONFIRMED_UNCAPPED
    )
    assert res["uncapped_status"] == STATUS_CONFIRMED_UNCAPPED
    assert res["is_eligible_uncapped"] is True
    assert res["age"] < 21.0
    assert "Under 21" in res["age_category"]
    assert res["is_young_uncapped"] is True


def test_uncapped_pool_filtering():
    """Verifies filtering by maximum age threshold and role."""
    df = pd.DataFrame([
        {"player_name": "Young Uncapped Batter", "dob": "2005-03-10", "playing_role": "Top-order Batter", "matches": 10, "uncapped_status": "Confirmed Uncapped"},
        {"player_name": "Veteran Domestic Batter", "dob": "1990-01-10", "playing_role": "Top-order Batter", "matches": 50, "uncapped_status": "Confirmed Uncapped"},
        {"player_name": "Virat Kohli", "dob": "1988-11-05", "playing_role": "Top-order Batter", "matches": 250, "uncapped_status": "Confirmed Uncapped"} # Capped override
    ])
    
    # Filter with max_age = 23.0
    pool = get_uncapped_player_pool(df, max_age=23.0, roles=["Top-order Batter"])
    names = pool["player_name"].tolist()
    
    assert "Young Uncapped Batter" in names
    assert "Veteran Domestic Batter" not in names  # Age > 23
    assert "Virat Kohli" not in names  # Capped international

