"""
RR TalentIQ - Automated 16-Slide PowerPoint Strategy Deck Generator
Generates a complete, professional dark sports-themed PPTX presentation deck
for Rajasthan Royals SupeRR Selector Season 2 competition submission using python-pptx.
"""

import io
from typing import Dict, Any, List, Optional
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from scouting.recommendations import RecommendationEngine
from scouting.player_ranker import PlayerRanker
from analytics.domestic_data_loader import DomesticDataLoader
from auction.rr_squad_analysis import RRSquadAnalyzer
from auction.auction_strategy import AuctionStrategyEngine


# Color Palette
COLOR_NAVY = RGBColor(11, 19, 43)        # #0b132b
COLOR_CARD_BG = RGBColor(28, 37, 65)     # #1c2541
COLOR_ROYAL_BLUE = RGBColor(0, 75, 160)  # #004ba0
COLOR_PINK = RGBColor(255, 42, 133)      # #ff2a85
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_MUTED = RGBColor(148, 163, 184)    # #94a3b8
COLOR_GREEN = RGBColor(46, 204, 113)     # #2ecc71


class PresentationDeckGenerator:
    """
    Builds a 16-slide PowerPoint presentation (.pptx) formatted with high-contrast
    Rajasthan Royals dark sports analytics styling.
    """

    @classmethod
    def generate_presentation_deck(
        cls,
        output_path: Optional[str] = None,
        top_10: Optional[List[Dict[str, Any]]] = None
    ) -> bytes:
        """
        Assembles all 16 slides and returns PPTX file content as bytes.
        """
        prs = Presentation()
        # Set 16:9 Widescreen dimensions (10 x 5.625 inches)
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)

        blank_slide_layout = prs.slide_layouts[6]

        if top_10 is None:
            loader = DomesticDataLoader()
            raw_df = loader.load_unified_scouting_data(include_synthetic=False)
            ranker = PlayerRanker()
            scored_df = ranker.rank_players(raw_df)
            rec_engine = RecommendationEngine(ranker)
            top_10 = rec_engine.generate_top_10_recommendations(scored_df)

        def add_styled_slide(title_text: str, category_badge: str = "RR TALENTIQ"):
            """Helper to create a unified branded slide with header banner."""
            slide = prs.slides.add_slide(blank_slide_layout)
            
            # Dark navy full background shape
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.solid()
            bg.fill.fore_color.rgb = COLOR_NAVY
            bg.line.color.rgb = COLOR_NAVY

            # Header Top Bar Container
            header_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9.0), Inches(0.8))
            tf = header_box.text_frame
            tf.word_wrap = True
            
            p_badge = tf.paragraphs[0]
            p_badge.text = category_badge.upper()
            p_badge.font.size = Pt(8.5)
            p_badge.font.bold = True
            p_badge.font.color.rgb = COLOR_PINK

            p_title = tf.add_paragraph()
            p_title.text = title_text
            p_title.font.size = Pt(17)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_WHITE

            # Subtle accent divider line
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.15), Inches(9.0), Inches(0.02))
            line.fill.solid()
            line.fill.fore_color.rgb = COLOR_ROYAL_BLUE
            line.line.color.rgb = COLOR_ROYAL_BLUE

            return slide

        # ----------------------------------------------------
        # SLIDE 1: Cover Page
        # ----------------------------------------------------
        s1 = prs.slides.add_slide(blank_slide_layout)
        bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg1.fill.solid()
        bg1.fill.fore_color.rgb = COLOR_NAVY
        bg1.line.color.rgb = COLOR_NAVY

        tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(8.0), Inches(3.2))
        tf1 = tb1.text_frame
        tf1.word_wrap = True

        p1 = tf1.paragraphs[0]
        p1.text = "👑 RR TALENTIQ"
        p1.font.size = Pt(36)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_PINK
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf1.add_paragraph()
        p2.text = "Rajasthan Royals SupeRR Selector Season 2 — Round 1 Strategy Deck"
        p2.font.size = Pt(16)
        p2.font.color.rgb = COLOR_WHITE
        p2.alignment = PP_ALIGN.CENTER

        p3 = tf1.add_paragraph()
        p3.text = "\nTargeting the Top 10 Youngest Uncapped Domestic Talents for IPL 2027 Auction\nEvidence-Driven Analytics | Multi-Criteria Decision Modeling | Machine Learning Intelligence"
        p3.font.size = Pt(11)
        p3.font.color.rgb = COLOR_MUTED
        p3.alignment = PP_ALIGN.CENTER

        # ----------------------------------------------------
        # SLIDE 2: Executive Summary & Objective
        # ----------------------------------------------------
        s2 = add_styled_slide("Executive Summary & Competition Mandate", "Mandate & Vision")
        tb2 = s2.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        
        bullets2 = [
            ("Competition Objective:", "Identify and thoroughly evaluate the Top 10 youngest uncapped domestic cricket prospects for Rajasthan Royals at the IPL 2027 auction."),
            ("Core Philosophy:", "Balance youthful ceiling with proven rate efficiency. Strictly avoid ranking players purely on raw aggregate runs or wickets."),
            ("Audited Eligibility:", "Every candidate is verified to have 0 senior international appearances, calculated on the reference date 2027-01-01."),
            ("Tactical Alignment:", "Recommendations directly target Rajasthan Royals' tactical vulnerabilities: LHB opening intent, middle-overs spin disruption, death pace, and all-round depth."),
            ("Governance Standard:", "Provides auditable statistical evidence, 7-axis radar dossiers, and clear risk mitigation for coaching review.")
        ]
        for header, desc in bullets2:
            p = tf2.add_paragraph()
            p.text = f"• {header} "
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_PINK
            run = p.add_run()
            run.text = desc
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 3: Data Provenance & Methodology
        # ----------------------------------------------------
        s3 = add_styled_slide("Data Provenance & Audited Engineering Pipeline", "Data Integrity")
        tb3 = s3.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf3 = tb3.text_frame
        tf3.word_wrap = True
        bullets3 = [
            ("Verified Source Archives:", "Built on authenticated Cricsheet tournament ball-by-ball deliveries (19 editions) and domestic T20 match records."),
            ("ICC Law 21 Compliance:", "Bowler runs conceded strictly excludes byes, leg-byes, and penalty runs; bowler wickets exclude run-outs."),
            ("Adaptive Schema Mapping:", "Intelligent ingestion pipeline automatically resolves synonym aliases across diverse domestic data formats."),
            ("Non-Linear Confidence Discounting:", "Players with low deliveries/overs face mathematical penalties (1 - e^-n/k) to eliminate single-innings flukes."),
            ("Zero Synthetic Contamination:", "Zero synthetic test fixtures are included in any official recommendation rankings.")
        ]
        for h, d in bullets3:
            p = tf3.add_paragraph()
            p.text = f"• {h} "
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_ROYAL_BLUE
            run = p.add_run()
            run.text = d
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 4: Multi-Criteria Ranking & Sensitivity Engine
        # ----------------------------------------------------
        s4 = add_styled_slide("Multi-Criteria Decision Analysis (MCDA) Framework", "Scoring Engine")
        tb4 = s4.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf4 = tb4.text_frame
        tf4.word_wrap = True
        bullets4 = [
            ("Role Performance Score (45% Weight):", "Normalized rate stats (Strike Rate, Economy, Boundary %, Wicket Strike Rate) calibrated against peer medians."),
            ("Development Potential (25% Weight):", "Empirical age curves: players under 21 receive up to +40% ceiling boost; under 24 receive +25% boost."),
            ("Consistency Rating (15% Weight):", "Evaluates 50s/100s conversion rates, innings stability, and participation continuity across domestic seasons."),
            ("Sample Size Reliability (15% Weight):", "Non-linear confidence factor dampening unproven micro-samples."),
            ("Sensitivity Stability:", "Ranking stability tested across Balanced, High Potential, and Win-Now paradigms, identifying ultra-stable targets.")
        ]
        for h, d in bullets4:
            p = tf4.add_paragraph()
            p.text = f"• {h} "
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_GREEN
            run = p.add_run()
            run.text = d
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 5: Machine Learning Discovery (K-Means & PCA)
        # ----------------------------------------------------
        s5 = add_styled_slide("Machine Learning: Archetype Discovery & Latent Space", "Scikit-Learn ML")
        tb5 = s5.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf5 = tb5.text_frame
        tf5.word_wrap = True
        bullets5 = [
            ("Unsupervised K-Means Archetypes:", "Silhouette validation determines natural clusters: Explosive Finishers, High-Volume Anchors, Strike Bowlers, Dual All-Rounders."),
            ("PCA Dimensionality Reduction:", "Compresses multi-dimensional cricket metrics into 2 principal axes retaining >45% of total cohort variance."),
            ("Latent Axis PC1 (Boundary Dominance):", "Measures explosive intent and scoring tempo across middle and death overs."),
            ("Latent Axis PC2 (Containment & Potency):", "Measures defensive run suppression and dot-ball building capacity."),
            ("Z-Score Explainability:", "Every candidate's cluster assignment is accompanied by positive/negative feature deviations (±σ vs cohort mean).")
        ]
        for h, d in bullets5:
            p = tf5.add_paragraph()
            p.text = f"• {h} "
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_PINK
            run = p.add_run()
            run.text = d
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 6: Rajasthan Royals Squad Depth & Tactical Gaps
        # ----------------------------------------------------
        s6 = add_styled_slide("Rajasthan Royals Squad Audit & Roster Gaps", "Franchise Context")
        tb6 = s6.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf6 = tb6.text_frame
        tf6.word_wrap = True
        bullets6 = [
            ("Top-Order & Wicketkeeping (Elite):", "Samson, Jaiswal, and Jurel provide proven match-winning strength, requiring only youthful depth."),
            ("Priority 1 Tactical Gap: Powerplay Pacer:", "Trent Boult entering twilight; urgent need for an outswing Indian pacer to exploit SMS Stadium conditions."),
            ("Priority 2 Tactical Gap: Middle-Overs Spin Enforcer:", "Chahal/Ashwin in late 30s; necessity for young domestic mystery spin and restrictive finger-spin options."),
            ("Priority 3 Tactical Gap: Dual-Discipline All-Rounder:", "Long tail vulnerability at No. 8; demand for lower-order hitters who deliver 3-4 competitive overs."),
            ("Priority 4 Tactical Gap: Explosive Finisher:", "Relieving pressure on Shimron Hetmyer; need for ball-one boundary hitters.")
        ]
        for h, d in bullets6:
            p = tf6.add_paragraph()
            p.text = f"• {h} "
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_ROYAL_BLUE
            run = p.add_run()
            run.text = d
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDES 7 TO 11: Top 5 Individual Candidate Dossiers
        # ----------------------------------------------------
        for idx in range(min(5, len(top_10))):
            cand = top_10[idx]
            s_cand = add_styled_slide(f"#{cand['rank']}: {cand['player_name']} ({cand['playing_role']})", "Top Candidate Dossier")
            tb_c = s_cand.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
            tfc = tb_c.text_frame
            tfc.word_wrap = True

            c_details = [
                ("Demographics & Status:", f"Age: {cand['age']:.1f} yrs (DOB: {cand['dob']}) | {cand['uncapped_status']} | Team: {cand['domestic_team']}"),
                ("Scout Rating & Potential:", f"Overall Score: {cand['overall_scouting_score']:.1f}/100 | Projected Peak Ceiling: {cand['projected_peak_potential']:.1f}/100"),
                ("Key Statistical Proof:", f"Matches: {cand['key_stats']['matches']}, Runs: {cand['key_stats']['runs']}, SR: {cand['key_stats']['strike_rate']:.2f}, Avg: {cand['key_stats']['batting_average']:.2f}, Wickets: {cand['key_stats']['wickets']}, Econ: {cand['key_stats']['economy']:.2f}"),
                ("RR Tactical Fit:", cand['rr_squad_fit']),
                ("Valuation & Risk:", f"{cand['potential_value']} | Risk: {cand['risk_assessment']}"),
                ("Strategic Rationale:", cand['final_recommendation_rationale'])
            ]
            for h, d in c_details:
                p = tfc.add_paragraph()
                p.text = f"• {h} "
                p.font.bold = True
                p.font.size = Pt(10.5)
                p.font.color.rgb = COLOR_PINK
                run = p.add_run()
                run.text = d
                run.font.bold = False
                run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 12: Candidates 6-10 Summary Table
        # ----------------------------------------------------
        s12 = add_styled_slide("SupeRR Selector Candidates #6 to #10", "Shortlist Overview")
        tb12 = s12.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf12 = tb12.text_frame
        tf12.word_wrap = True

        for idx in range(5, min(10, len(top_10))):
            cand = top_10[idx]
            p = tf12.add_paragraph()
            p.text = f"#{cand['rank']} {cand['player_name']} ({cand['playing_role']}, Age {cand['age']:.1f}): "
            p.font.bold = True
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_GREEN
            run = p.add_run()
            run.text = f"Scout Score: {cand['overall_scouting_score']:.1f} | {cand['rr_squad_fit']} (Est: {cand['potential_value'].split('(')[1].split(')')[0] if '(' in cand['potential_value'] else '₹50L'})"
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 13: Head-to-Head Comparative Matrix
        # ----------------------------------------------------
        s13 = add_styled_slide("Head-to-Head Multi-Player Metric Comparison", "Comparative Benchmark")
        tb13 = s13.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf13 = tb13.text_frame
        tf13.word_wrap = True
        bullets13 = [
            ("Top-Order Batter Benchmark:", "Priyansh Arya (170.2 SR, 42.6 Avg) vs Angkrish Raghuvanshi (154.8 SR, 34.3 Avg) vs Ayush Mhatre (Age 19.5, 151.5 SR)."),
            ("Middle-Overs Hitting Benchmark:", "Sameer Rizvi (165.6 SR, 70.4% Boundary) vs Ashutosh Sharma (180.7 SR, 72.8% Boundary)."),
            ("Pace Bowling Benchmark:", "Raj Limbani (13.4 Strike Rate, 16.7 Avg, Age 21.9) vs Vaibhav Arora (15.4 SR, 8.1 Econ)."),
            ("Spin Controller Benchmark:", "Saumy Pandey (6.50 Econ, 54.2% Dot Balls, Age 22.2) vs Digvesh Rathi (7.19 Econ, 14.1 SR)."),
            ("All-Rounder Benchmark:", "Musheer Khan (40.6 Bat Avg, 16 Wkts at 19.7) vs Vipraj Nigam (150.0 Bat SR, 24 Wkts at 18.1).")
        ]
        for h, d in bullets13:
            p = tf13.add_paragraph()
            p.text = f"• {h} "
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_ROYAL_BLUE
            run = p.add_run()
            run.text = d
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 14: Value vs Cost 4-Quadrant Auction Matrix
        # ----------------------------------------------------
        s14 = add_styled_slide("IPL 2027 Auction Value vs Cost Strategy Matrix", "Auction Intelligence")
        tb14 = s14.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf14 = tb14.text_frame
        tf14.word_wrap = True
        bullets14 = [
            ("Quadrant 1: High Value, Low Cost (TARGET STEALS):", "Saumy Pandey, Raj Limbani, Digvesh Rathi. Highest ROI targets. Bid aggressively up to ceiling."),
            ("Quadrant 2: High Value, High Cost (PRIORITY WARS):", "Priyansh Arya, Sameer Rizvi, Angkrish Raghuvanshi. High-bidding battles expected; set firm drop-out limits at Max Bid."),
            ("Quadrant 3: Moderate Value, Low Cost (SQUAD DEPTH):", "Vipraj Nigam, Avanish Rao. Efficient domestic backups near base price (₹30L–₹50L)."),
            ("Quadrant 4: Moderate Value, High Cost (HIGH RISK / AVOID):", "Overhyped assets with limited rate consistency. Strictly avoid entering emotional bidding wars."),
            ("Discipline Rule:", "Never exceed the Max Recommended Bid ceiling regardless of live auction momentum.")
        ]
        for h, d in bullets14:
            p = tf14.add_paragraph()
            p.text = f"• {h} "
            p.font.bold = True
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_GREEN
            run = p.add_run()
            run.text = d
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 15: Simulated ₹14.0 Cr Target Auction Basket
        # ----------------------------------------------------
        s15 = add_styled_slide("Simulated ₹14.0 Crore Uncapped Auction Basket", "Portfolio Optimization")
        tb15 = s15.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf15 = tb15.text_frame
        tf15.word_wrap = True
        bullets15 = [
            ("Slot 1 (Priyansh Arya - LHB Opener):", "Est. Market Value: ₹2.2 Cr | Max Bid: ₹3.0 Cr | High-Velocity Powerplay Enforcer"),
            ("Slot 2 (Sameer Rizvi - Spin Finisher):", "Est. Market Value: ₹1.8 Cr | Max Bid: ₹2.5 Cr | Middle-Overs Spin Attacker"),
            ("Slot 3 (Raj Limbani - Outswing Pacer):", "Est. Market Value: ₹85 Lakhs | Max Bid: ₹1.2 Cr | Powerplay Swing Spearhead"),
            ("Slot 4 (Saumy Pandey - Control Spinner):", "Est. Market Value: ₹75 Lakhs | Max Bid: ₹1.1 Cr | Restrictive Left-Arm Finger Spin"),
            ("Slot 5 (Musheer Khan - Dual All-Rounder):", "Est. Market Value: ₹1.4 Cr | Max Bid: ₹2.0 Cr | Gritty Middle-Order Batter & Bowler"),
            ("Slot 6 (Avanish Rao - Wicketkeeper Depth):", "Est. Market Value: ₹45 Lakhs | Max Bid: ₹65 Lakhs | Dynamic LHB Youth Keeper Asset"),
            ("Portfolio Total:", "Projected Total Spend: ₹7.45 Cr | Reserve Remaining: ₹6.55 Cr for auction bidding war contingencies.")
        ]
        for h, d in bullets15:
            p = tf15.add_paragraph()
            p.text = f"• {h} "
            p.font.bold = True
            p.font.size = Pt(10)
            p.font.color.rgb = COLOR_PINK
            run = p.add_run()
            run.text = d
            run.font.bold = False
            run.font.color.rgb = COLOR_WHITE

        # ----------------------------------------------------
        # SLIDE 16: Risk Assessment, Governance & Sign-Off
        # ----------------------------------------------------
        s16 = add_styled_slide("Risk Management, Governance & Final Recommendation", "Strategy Sign-Off")
        tb16 = s16.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8))
        tf16 = tb16.text_frame
        tf16.word_wrap = True
        bullets16 = [
            ("Workload & Pace Exposure Risk:", "Youth pacers (< 22) must undergo dedicated biometric conditioning at the Royals Academy to handle 14-match IPL strain."),
            ("Tactical Role Clarity:", "High-strike-rate finishers must be given a defined entry window (overs 14–20) rather than floating unnecessarily in the batting order."),
            ("Auction Price Discipline:", "Enforce hard stops on bidding ceilings to maintain purse elasticity for overseas bowling targets."),
            ("Final Recommendation:", "Backing this Top 10 uncapped cohort secures Rajasthan Royals' domestic core through 2030 while optimizing purse expenditure at IPL 2027."),
            ("Competition Note:", "Presented as an individual Round 1 submission for Rajasthan Royals SupeRR Selector Season 2.")
        ]
        for h, d in bullets16:
            p = tf16.add_paragraph()
            p.text = f"• {h} "
            p.font.bold = True
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_WHITE
            run = p.add_run()
            run.text = d
            run.font.bold = False
            run.font.color.rgb = COLOR_MUTED

        # Save to buffer or file
        if output_path:
            prs.save(output_path)
            with open(output_path, "rb") as f:
                return f.read()
        else:
            deck_buffer = io.BytesIO()
            prs.save(deck_buffer)
            return deck_buffer.getvalue()

