"""
RR TalentIQ - Top 10 Youngest Uncapped Recommendation Engine
Curates, audits, and ranks the Top 10 youngest uncapped domestic prospects
for Rajasthan Royals for the IPL 2027 Auction (SupeRR Selector Season 2).
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scouting.player_ranker import PlayerRanker
from scouting.player_profiles import PlayerProfileEngine
from scouting.uncapped_filter import get_uncapped_player_pool


# RR Tactical Archetype Fit Matrix for IPL 2027 Auction
# Rajasthan Royals tactical profile: Explosive openers, middle-overs spin disruptors, death pacers, versatile all-rounders
RR_TACTICAL_FIT_RATIONALE = {
    "Priyansh Arya": {
        "rr_squad_fit": "Aggressive LHB Powerplay Batter. Ideal backup and future opening successor alongside Yashasvi Jaiswal, providing blistering intent from ball one.",
        "potential_value": "High Auction Ceiling (₹1.5 Cr – ₹3.5 Cr projected). High demand for dynamic uncapped Indian LH openers.",
        "risk_assessment": "Moderate. Faces testing high pace bouncers on bouncy Sawai Mansingh Stadium tracks.",
        "final_recommendation_rationale": "Dominant DPL & SMAT scoring rate (170.17 SR, 2 centuries); solves RR's requirement for top-order boundary intent."
    },
    "Sameer Rizvi": {
        "rr_squad_fit": "Middle-Overs Spin Enforcer & Power Finisher. Natural fit for RR's middle order (Nos. 4–6) to attack opposition finger and wrist spin.",
        "potential_value": "High Value Investment (₹1.2 Cr – ₹2.5 Cr). Rare Indian power-hitting commodity with proven T20 boundary percentages.",
        "risk_assessment": "Low-to-Moderate. Requires designated role clarity without floating across multiple positions.",
        "final_recommendation_rationale": "Elite 165.62 SR, 44.17 Average, and 70.4% boundary run contribution; possesses rare raw bat speed suited for Jaipur boundaries."
    },
    "Angkrish Raghuvanshi": {
        "rr_squad_fit": "Class Top-Order Anchor / No. 3 Batter. Possesses complete technical repertoire to navigate swinging new balls and steady early collapses.",
        "potential_value": "Exceptional Long-Term Core (₹1.5 Cr – ₹3.0 Cr). Youth asset (age 21.6) with decade-long franchise potential.",
        "risk_assessment": "Low. Technologically sound Mumbai pedigree with proven big-match composure under pressure.",
        "final_recommendation_rationale": "Combines 154.84 SR with 34.28 Average at age 21.6; offers fielding agility and auxiliary left-arm spin option."
    },
    "Raj Limbani": {
        "rr_squad_fit": "Outswing Powerplay Pacer. Perfect bowling partner to exploit early lateral swing and movement with the new ball at SMS Stadium.",
        "potential_value": "High ROI Fast-Bowling Steal (₹40 L – ₹1.2 Cr). Age 21.9 genuine new-ball wicket-taker.",
        "risk_assessment": "Moderate. Needs physical workload conditioning for long 14-match IPL tournament grueling.",
        "final_recommendation_rationale": "Phenomenal 13.38 bowling strike rate and 16.73 average in youth/domestic ranks; moves ball both ways at good pace."
    },
    "Saumy Pandey": {
        "rr_squad_fit": "Control Left-Arm Orthodox Spinner. Natural strategic counterpart to Yuzvendra Chahal / Ravichandran Ashwin, offering strangulating middle-overs economy.",
        "potential_value": "Defensive Anchor Buy (₹50 L – ₹1.5 Cr). Age 22.2 defensive spin controller.",
        "risk_assessment": "Low. Highly disciplined line and length with minimal boundary leakage.",
        "final_recommendation_rationale": "Economy rate of 6.50 and 13.71 strike rate; suppresses dot balls to 54.2% across competitive domestic overs."
    },
    "Ayush Mhatre": {
        "rr_squad_fit": "Future Prodigy Top-Order Batter. Youngest elite uncapped batter in the pool (age 19.5), providing long-term developmental insurance.",
        "potential_value": "Long-Term Foundation Asset (₹30 L – ₹1.0 Cr). Highest ceiling growth curve in domestic cricket.",
        "risk_assessment": "Moderate. Young raw domestic sample requiring patient nurturing within the Royals Academy.",
        "final_recommendation_rationale": "Scored domestic hundreds before age 20 with 151.47 SR; high-ceiling generational batting talent."
    },
    "Musheer Khan": {
        "rr_squad_fit": "Combative No. 4/5 Batting All-Rounder. Provides gritty temperament, middle-order run accumulation, and 2-3 reliable overs of left-arm orthodox.",
        "potential_value": "Elite All-Round Utility (₹1.0 Cr – ₹2.5 Cr). Proven domestic match-winner in knockout situations.",
        "risk_assessment": "Low. Exceptional game awareness and pressure-absorber; recovering strongly from past injury.",
        "final_recommendation_rationale": "40.63 batting average combined with 16 wickets at 19.69; possesses the classic fighting Royals DNA."
    },
    "Vipraj Nigam": {
        "rr_squad_fit": "Attacking Leg-Spin All-Rounder. Provides aggressive lower-order batting at No. 8 and deceptive wicket-taking wrist spin.",
        "potential_value": "High-Upside Domestic Sleeper (₹40 L – ₹1.0 Cr). Dual-discipline wrist-spin package.",
        "risk_assessment": "Moderate. Can be occasionally expensive if lengths are missed on flat tracks.",
        "final_recommendation_rationale": "Strike rate of 14.50 with ball (24 wickets) plus 150.00 SR with bat; fills a rare tactical niche for domestic wrist-spin depth."
    },
    "Aravelly Avanish Rao": {
        "rr_squad_fit": "Dynamic LHB Wicketkeeper-Finisher. Direct positional backup and competitor in wicketkeeping slots, adding left-handed variety.",
        "potential_value": "High-Growth Keeper Asset (₹30 L – ₹80 L). Clean glovework technician at age 21.6.",
        "risk_assessment": "Low-to-Moderate. Requires top-level coaching on death-overs yorker execution.",
        "final_recommendation_rationale": "144.52 SR with 25 dismissals (including 6 sharp stumpings); solves wicketkeeping depth with high youth ceiling."
    },
    "Digvesh Rathi": {
        "rr_squad_fit": "Middle-Overs Mystery Leg-Spinner. Exploits large Jaipur boundary dimensions with sharp turn and deceptive googlies.",
        "potential_value": "Tactical Buy (₹30 L – ₹90 L). Low economy (7.19) legbreak specialist.",
        "risk_assessment": "Moderate. Faces intense batter analysis once tape becomes widely available.",
        "final_recommendation_rationale": "23 wickets in 15 games at 14.09 strike rate; restricts batters through 46.9% dot-ball build-up."
    }
}


class RecommendationEngine:
    """
    Produces the final, evidence-driven Top 10 Youngest Uncapped recommendations
    for Rajasthan Royals SupeRR Selector Season 2 submission.
    """

    def __init__(self, ranker: Optional[PlayerRanker] = None):
        self.ranker = ranker or PlayerRanker()

    def generate_top_10_recommendations(
        self,
        df: pd.DataFrame,
        max_age: float = 26.0,
        min_matches: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Executes multi-tier qualification and ranking to extract the Top 10 recommendations.
        
        Selection criteria:
        1. Confirmed uncapped domestic status (0 international senior caps).
        2. Age criteria: Youngest prospects (prioritizing under 24, ceiling at 26).
        3. Statistical merit: High Overall Scouting Score with proven sample confidence.
        4. Tactical balance: Covers top-order batting, finishing, wicketkeeping, pace, spin, and all-rounders.
        """
        # Step 1: Filter to eligible uncapped domestic pool
        uncapped_df = get_uncapped_player_pool(df, max_age=max_age, min_matches=min_matches)
        
        # Step 2: Rank players using standard multi-criteria scoring
        ranked_df = self.ranker.rank_players(uncapped_df)

        # Step 3: Extract top candidates
        top_candidates = ranked_df.head(15).copy()

        # Step 4: Assemble top 10 profiles with tactical fit justifications
        recommendations = []
        for rank_idx, (_, row) in enumerate(top_candidates.iterrows()):
            if len(recommendations) >= 10:
                break
                
            p_name = row["player_name"]
            dossier = PlayerProfileEngine.generate_player_dossier(row)
            
            # Enrich with RR Tactical Fit Rationale
            tactical_info = RR_TACTICAL_FIT_RATIONALE.get(p_name, {
                "rr_squad_fit": f"Fills depth requirements in the {row['playing_role']} department with high youth potential.",
                "potential_value": "Estimated Base to Moderate Auction Price (₹30 L – ₹80 L).",
                "risk_assessment": "Moderate. Requires exposure to elite franchise training camps.",
                "final_recommendation_rationale": f"High Overall Scouting Score ({row['overall_scouting_score']:.1f}) backed by consistent domestic execution."
            })

            rec_item = {
                "rank": len(recommendations) + 1,
                "player_id": dossier["player_id"],
                "player_name": p_name,
                "dob": dossier["dob"],
                "age": dossier["age"],
                "uncapped_status": dossier["uncapped_status"],
                "playing_role": dossier["playing_role"],
                "batting_style": dossier["batting_style"],
                "bowling_style": dossier["bowling_style"],
                "domestic_team": dossier["domestic_team"],
                "overall_scouting_score": dossier["overall_scouting_score"],
                "role_performance_score": dossier["role_performance_score"],
                "projected_peak_potential": dossier["projected_peak_potential"],
                "consistency_score": dossier["consistency_score"],
                "key_stats": {
                    "matches": dossier["matches"],
                    "runs": dossier["runs"],
                    "strike_rate": dossier["strike_rate"],
                    "batting_average": dossier["batting_average"],
                    "wickets": dossier["wickets"],
                    "economy": dossier["economy"],
                    "bowling_strike_rate": dossier["bowling_strike_rate"],
                    "catches": dossier["catches"],
                    "stumpings": dossier["stumpings"]
                },
                "strengths": dossier["strengths"][:3],
                "weaknesses": dossier["weaknesses"][:2],
                "rr_squad_fit": tactical_info["rr_squad_fit"],
                "potential_value": tactical_info["potential_value"],
                "risk_assessment": tactical_info["risk_assessment"],
                "final_recommendation_rationale": tactical_info["final_recommendation_rationale"],
                "requires_human_approval": True,
                "data_source": dossier["data_source"]
            }
            recommendations.append(rec_item)

        return recommendations

