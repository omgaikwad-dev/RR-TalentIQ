"""
RR TalentIQ - Age & Eligibility Engine
Calculates precise player age relative to the target auction/season reference date,
audits date-of-birth integrity, and evaluates uncapped eligibility status for IPL 2027.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

# Official Target Reference Date for IPL 2027 Auction & Season Planning
DEFAULT_AGE_REFERENCE_DATE = "2027-01-01"

# Uncapped Status Definitions
STATUS_CONFIRMED_UNCAPPED = "Confirmed Uncapped"
STATUS_POTENTIALLY_UNCAPPED = "Potentially Uncapped"
STATUS_CAPPED = "Capped"
STATUS_UNKNOWN = "Unknown Status"

# List of known capped Indian international players to guard against misclassification
KNOWN_CAPPED_INDIAN_PLAYERS = {
    "V Kohli", "Virat Kohli", "Rg Sharma", "Rohit Sharma", "J Bumrah", "Jasprit Bumrah",
    "R Ashwin", "Ravichandran Ashwin", "Ra Jadeja", "Ravindra Jadeja", "Kl Rahul", "K L Rahul",
    "S Dhawan", "Shikhar Dhawan", "Mohammed Shami", "M Shami", "B Kumar", "Bhuvneshwar Kumar",
    "Kuldeep Yadav", "Ys Chahal", "Yuzvendra Chahal", "Axar Patel", "A Patel", "Hardik Pandya",
    "H Pandya", "Suryakumar Yadav", "Sk Yadav", "Shreyas Iyer", "Ss Iyer", "Rishabh Pant",
    "R Pant", "Sanju Samson", "Sv Samson", "Ishan Kishan", "I Kishan", "Shubman Gill",
    "S Gill", "Yashasvi Jaiswal", "Ybk Jaiswal", "Mohammed Siraj", "M Siraj", "Arshdeep Singh",
    "Washington Sundar", "W Sundar", "Rinku Singh", "Tilak Varma", "Shivam Dube", "S Dube",
    "Jitesh Sharma", "Mukesh Kumar", "Avesh Khan", "Prasidh Krishna", "Umran Malik",
    "Ravi Bishnoi", "Ruturaj Gaikwad", "Devdutt Padikkal", "Chetan Sakariya", "Varun Chakravarthy",
    "Rajat Patidar", "Nitish Kumar Reddy", "Mayank Yadav", "Harshit Rana", "Dhruv Jurel"
}


class AgeEligibilityEngine:
    """
    Validates, calculates, and audits player age and uncapped eligibility
    for Rajasthan Royals talent scouting and auction planning.
    """

    def __init__(self, reference_date: str = DEFAULT_AGE_REFERENCE_DATE):
        self.reference_date_str = reference_date
        self.reference_date = datetime.strptime(reference_date, "%Y-%m-%d")

    def calculate_exact_age(self, dob_val: Any) -> Tuple[Optional[float], str]:
        """
        Computes decimal age on reference date from a date of birth.
        Returns (age_decimal, audit_note).
        """
        if dob_val is None or pd.isna(dob_val) or str(dob_val).strip() in ["", "Unknown", "nan", "NaT"]:
            return None, "Missing Date of Birth"
        
        try:
            parsed_dob = pd.to_datetime(dob_val)
            if pd.isna(parsed_dob):
                return None, "Unparseable Date format"
            
            delta_days = (self.reference_date - parsed_dob).days
            if delta_days < 0:
                return None, "Future Date of Birth detected (Invalid)"
            
            exact_age = round(delta_days / 365.25, 2)
            if exact_age < 14.0 or exact_age > 46.0:
                return exact_age, f"Out-of-range Age Warning: {exact_age} years"
            
            return exact_age, "Verified DOB"
        except Exception as e:
            return None, f"Parsing exception: {str(e)}"

    def evaluate_player_eligibility(
        self,
        player_name: str,
        dob_val: Any = None,
        provided_age: Any = None,
        provided_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs an auditable eligibility check for an individual player.
        """
        norm_name = str(player_name).strip()
        calculated_age, dob_note = self.calculate_exact_age(dob_val)
        
        # Age reconciliation
        final_age = calculated_age
        age_conflict = False
        if final_age is None and provided_age is not None and not pd.isna(provided_age):
            try:
                final_age = round(float(provided_age), 1)
                dob_note = "Age sourced from provided age field (DOB missing)"
            except (ValueError, TypeError):
                final_age = None
        elif final_age is not None and provided_age is not None and not pd.isna(provided_age):
            try:
                p_age = float(provided_age)
                if abs(final_age - p_age) > 1.5:
                    age_conflict = True
                    dob_note = f"Age Conflict: Calculated {final_age} vs Provided {p_age}"
            except (ValueError, TypeError):
                pass

        # Capped vs Uncapped evaluation
        if norm_name in KNOWN_CAPPED_INDIAN_PLAYERS:
            uncapped_status = STATUS_CAPPED
            eligibility_note = "Player has represented India senior men's team (Capped)"
            is_eligible_for_uncapped_pick = False
        elif provided_status == STATUS_CAPPED:
            uncapped_status = STATUS_CAPPED
            eligibility_note = "Marked as Capped in input dataset"
            is_eligible_for_uncapped_pick = False
        elif provided_status == STATUS_CONFIRMED_UNCAPPED:
            uncapped_status = STATUS_CONFIRMED_UNCAPPED
            eligibility_note = "Confirmed domestic uncapped cricketer"
            is_eligible_for_uncapped_pick = True
        elif provided_status == STATUS_POTENTIALLY_UNCAPPED:
            uncapped_status = STATUS_POTENTIALLY_UNCAPPED
            eligibility_note = "Potentially uncapped - pending international cap verification"
            is_eligible_for_uncapped_pick = True
        else:
            uncapped_status = STATUS_CONFIRMED_UNCAPPED
            eligibility_note = "Defaulted to Confirmed Uncapped based on domestic profile"
            is_eligible_for_uncapped_pick = True

        # Young talent bracket assessment (Competition focus: youngest uncapped players)
        # Category A: Under 21 (< 21.0)
        # Category B: 21 - 23.9
        # Category C: 24 - 26.9
        # Category D: 27+
        age_category = "Unknown"
        is_young_uncapped = False
        if final_age is not None:
            if final_age < 21.0:
                age_category = "Under 21 (Elite Youth)"
                is_young_uncapped = True
            elif final_age < 24.0:
                age_category = "21–23 (Prime Young Talent)"
                is_young_uncapped = True
            elif final_age < 27.0:
                age_category = "24–26 (Peak Emerging)"
                is_young_uncapped = False
            else:
                age_category = "27+ (Experienced Domestic)"
                is_young_uncapped = False

        return {
            "player_name": norm_name,
            "dob": str(dob_val) if dob_val and not pd.isna(dob_val) else "Unknown",
            "age": final_age,
            "reference_date": self.reference_date_str,
            "dob_audit_note": dob_note,
            "age_conflict": age_conflict,
            "uncapped_status": uncapped_status,
            "is_eligible_uncapped": is_eligible_for_uncapped_pick,
            "age_category": age_category,
            "is_young_uncapped": is_young_uncapped,
            "eligibility_note": eligibility_note
        }

    def audit_dataset_eligibility(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches an entire player dataframe with standardized age and eligibility audit columns.
        """
        results = []
        for _, row in df.iterrows():
            name = row.get("player_name", "")
            dob = row.get("dob", None)
            prov_age = row.get("age", None)
            status = row.get("uncapped_status", None)
            
            res = self.evaluate_player_eligibility(name, dob, prov_age, status)
            results.append(res)
            
        audit_df = pd.DataFrame(results)
        
        # Merge back onto original dataframe
        enriched = df.copy()
        enriched["age"] = audit_df["age"]
        enriched["age_reference_date"] = self.reference_date_str
        enriched["uncapped_status"] = audit_df["uncapped_status"]
        enriched["is_eligible_uncapped"] = audit_df["is_eligible_uncapped"]
        enriched["age_category"] = audit_df["age_category"]
        enriched["is_young_uncapped"] = audit_df["is_young_uncapped"]
        enriched["dob_audit_note"] = audit_df["dob_audit_note"]
        enriched["age_conflict"] = audit_df["age_conflict"]
        return enriched

