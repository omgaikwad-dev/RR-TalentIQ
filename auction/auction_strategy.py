"""
RR TalentIQ - Auction Strategy & Value-vs-Cost Optimization Engine
Generates budget allocation scenarios, strategic quadrants,
and Value-vs-Cost prioritization models for the IPL 2027 auction.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from auction.player_valuation import PlayerValuationEngine


# Hypothetical Unverified Auction Purse Benchmark for IPL 2027 Cycle
BENCHMARK_TOTAL_PURSE_CRORES = 120.0
BENCHMARK_RETAINED_DEDUCTION_CRORES = 79.0  # Estimated deduction for 5-6 elite retentions
ESTIMATED_AUCTION_PURSE_CRORES = 41.0
TARGET_UNCAPPED_BUDGET_CRORES = 14.0       # Recommended allocation for uncapped domestic slots (5-7 players)


class AuctionStrategyEngine:
    """
    Formulates portfolio budget allocations and value-versus-cost quadrant classification.
    """

    @staticmethod
    def get_budget_overview() -> Dict[str, Any]:
        """Returns the working auction budget framework with verified/unverified disclaimers."""
        return {
            "total_hypothetical_purse_cr": BENCHMARK_TOTAL_PURSE_CRORES,
            "retained_salary_deduction_cr": BENCHMARK_RETAINED_DEDUCTION_CRORES,
            "available_auction_purse_cr": ESTIMATED_AUCTION_PURSE_CRORES,
            "target_uncapped_allocation_cr": TARGET_UNCAPPED_BUDGET_CRORES,
            "recommended_uncapped_slots": "5 to 7 domestic players",
            "is_official_bcci_confirmed": False,
            "disclaimer": "IPL 2027 auction purse rules and retention deduction amounts are unverified projections based on historical IPL governing council trends."
        }

    @classmethod
    def classify_value_vs_cost_quadrants(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Partitions players into strategic auction quadrants based on
        Overall Scouting Score (Value) vs Estimated Market Value (Cost).
        """
        # Ensure valuations are attached
        if "estimated_market_value_lakhs" not in df.columns:
            v_df = PlayerValuationEngine.attach_valuations_to_dataset(df)
        else:
            v_df = df.copy()

        # Quadrant Thresholds
        val_median = 75.0   # High vs Moderate Scouting Score threshold
        cost_median = 100.0 # High vs Moderate EMV threshold (₹1.0 Cr)

        quadrants = []
        strategic_actions = []

        for _, row in v_df.iterrows():
            oss = float(row.get("overall_scouting_score", 50.0) or 50.0)
            cost = float(row.get("estimated_market_value_lakhs", 50.0) or 50.0)

            if oss >= val_median and cost <= cost_median:
                quadrants.append("Quadrant 1: High Value, Low Cost (Target Steals)")
                strategic_actions.append("Primary Target: Bid aggressively up to recommended ceiling. High ROI guarantee.")
            elif oss >= val_median and cost > cost_median:
                quadrants.append("Quadrant 2: High Value, High Cost (Priority Battles)")
                strategic_actions.append("Core Investment: Prepare for multi-team bidding war. Set strict drop-out threshold at max bid.")
            elif oss < val_median and cost <= cost_median:
                quadrants.append("Quadrant 3: Moderate Value, Low Cost (Squad Depth)")
                strategic_actions.append("Bench Depth: Target near base price (₹30L–₹50L) for reserve role insurance.")
            else:
                quadrants.append("Quadrant 4: Moderate Value, High Cost (High Risk / Avoid)")
                strategic_actions.append("Caution: High hype-to-performance ratio. Avoid entering bidding wars.")

        v_df["auction_quadrant"] = quadrants
        v_df["strategic_action"] = strategic_actions
        return v_df

    @classmethod
    def assemble_target_auction_cart(
        cls,
        df: pd.DataFrame,
        budget_limit_lakhs: float = TARGET_UNCAPPED_BUDGET_CRORES * 100.0,
        max_picks: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Simulates an optimized auction basket of uncapped domestic players
        maximizing squad fit and tactical balance within budget constraints.
        """
        quad_df = cls.classify_value_vs_cost_quadrants(df)
        # Prioritize Quadrant 1 (Steals), then Quadrant 2 (Core Priorities)
        sorted_targets = quad_df.sort_values(
            by=["overall_scouting_score", "estimated_market_value_lakhs"],
            ascending=[False, True]
        )

        cart = []
        running_cost = 0.0
        covered_roles = set()

        for _, row in sorted_targets.iterrows():
            if len(cart) >= max_picks:
                break

            cost = float(row["estimated_market_value_lakhs"])
            role = str(row["playing_role"])

            # Check budget feasibility
            if running_cost + cost <= budget_limit_lakhs:
                cart.append({
                    "slot": len(cart) + 1,
                    "player_name": row["player_name"],
                    "playing_role": role,
                    "age": row.get("age", None),
                    "overall_scouting_score": row["overall_scouting_score"],
                    "estimated_market_value_lakhs": cost,
                    "max_bid_lakhs": row["max_recommended_bid_lakhs"],
                    "auction_quadrant": row["auction_quadrant"]
                })
                running_cost += cost
                covered_roles.add(role)

        return cart

