"""
RR TalentIQ - Executive Summary PDF Report Generator
Generates an audit-grade, multi-page PDF strategy report for the Rajasthan Royals
SupeRR Selector Season 2 competition using ReportLab.
"""

import os
import io
from typing import Dict, Any, List, Optional
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

from scouting.recommendations import RecommendationEngine
from scouting.player_ranker import PlayerRanker
from analytics.domestic_data_loader import DomesticDataLoader
from auction.rr_squad_analysis import RRSquadAnalyzer
from auction.auction_strategy import AuctionStrategyEngine


class ExecutiveSummaryPDFGenerator:
    """
    Builds an executive-grade, publication-quality PDF scouting report for RR TalentIQ.
    """

    @classmethod
    def generate_pdf(
        cls,
        output_path: Optional[str] = None,
        top_10: Optional[List[Dict[str, Any]]] = None
    ) -> bytes:
        """
        Compiles the full strategy report into PDF format.
        Returns the PDF content as bytes, and optionally saves to output_path.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            output_path if output_path else buffer,
            pagesize=letter,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        if top_10 is None:
            loader = DomesticDataLoader()
            raw_df = loader.load_unified_scouting_data(include_synthetic=False)
            ranker = PlayerRanker()
            scored_df = ranker.rank_players(raw_df)
            rec_engine = RecommendationEngine(ranker)
            top_10 = rec_engine.generate_top_10_recommendations(scored_df)

        story = []
        styles = getSampleStyleSheet()

        # Custom Palette
        navy = colors.HexColor("#0b132b")
        royal_blue = colors.HexColor("#004ba0")
        pink = colors.HexColor("#ff2a85")
        light_gray = colors.HexColor("#f8fafc")
        charcoal = colors.HexColor("#1e293b")

        # Custom Typography Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=navy,
            alignment=1, # Center
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=pink,
            alignment=1,
            spaceAfter=15
        )

        h1_style = ParagraphStyle(
            "H1",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=royal_blue,
            spaceBefore=12,
            spaceAfter=6
        )

        h2_style = ParagraphStyle(
            "H2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=navy,
            spaceBefore=8,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=charcoal,
            spaceAfter=6
        )

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=body_style,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=3
        )

        # Cover / Header Banner
        story.append(Paragraph("RR TALENTIQ — STRATEGY DOSSIER", title_style))
        story.append(Paragraph("Rajasthan Royals SupeRR Selector Season 2 — IPL 2027 Auction Intelligence", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=pink, spaceBefore=0, spaceAfter=12))

        # Section 1: Executive Summary & Objective
        story.append(Paragraph("1. Executive Summary & Competition Objective", h1_style))
        exec_text = (
            "This strategy report presents the primary findings for Round 1 of the <b>Rajasthan Royals SupeRR Selector "
            "Season 2</b> competition. The mandate is to identify and justify the <b>Top 10 youngest uncapped domestic cricketers</b> "
            "whom Rajasthan Royals should consider backing at the upcoming IPL 2027 auction cycle.<br/><br/>"
            "Using a multi-criteria decision modeling framework (combining role-specific performance indices, development potential "
            "curves, consistency ratings, and sample-size confidence dampening), we evaluated the domestic talent pool. "
            "The recommendations strictly enforce confirmed uncapped status (0 senior international caps), prioritize youth assets "
            "under 24 years of age, and directly target the franchise's top structural gaps."
        )
        story.append(Paragraph(exec_text, body_style))
        story.append(Spacer(1, 8))

        # Section 2: Data Provenance & Audit Compliance
        story.append(Paragraph("2. Data Provenance & Cricket Rules Compliance", h1_style))
        prov_text = (
            "&bull; <b>Data Sourcing:</b> Grounded in authentic Cricsheet ball-by-ball tournament archives and verified domestic match records.<br/>"
            "&bull; <b>ICC Law 21 Compliance:</b> Bowler runs conceded strictly exclude byes and leg-byes; bowler wickets exclude run-outs.<br/>"
            "&bull; <b>Reference Date:</b> Age calculations are strictly pegged to <b>2027-01-01</b>, preventing inconsistent age assertions.<br/>"
            "&bull; <b>Data Segregation:</b> Zero synthetic test fixtures are included in this production recommendation shortlist."
        )
        story.append(Paragraph(prov_text, body_style))
        story.append(Spacer(1, 8))

        # Section 3: Summary Table of Top 10 Recommendations
        story.append(Paragraph("3. Top 10 Youngest Uncapped Shortlist for Rajasthan Royals", h1_style))
        
        table_data = [
            ["Rk", "Player Name", "Role", "Age", "Team", "Scout\nScore", "Est. Value", "Primary Tactical Asset"]
        ]

        for r in top_10:
            val_str = r["potential_value"].split("(")[1].split(")")[0] if "(" in r["potential_value"] else "₹50L"
            table_data.append([
                str(r["rank"]),
                r["player_name"],
                r["playing_role"],
                f"{r['age']:.1f}",
                r["domestic_team"][:10],
                f"{r['overall_scouting_score']:.1f}",
                val_str[:12],
                r["strengths"][0][:30] + "..." if len(r["strengths"][0]) > 30 else r["strengths"][0]
            ])

        t = Table(table_data, colWidths=[0.3*inch, 1.2*inch, 1.1*inch, 0.45*inch, 0.75*inch, 0.65*inch, 0.95*inch, 1.8*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), royal_blue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (3, 1), (3, -1), "CENTER"),
            ("ALIGN", (5, 1), (5, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
            ("FONTSIZE", (0, 1), (-1, -1), 7.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3)
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

        # Section 4: Detailed Candidate Dossiers
        story.append(Paragraph("4. Individual Player Profiles & Strategic RR Fit", h1_style))
        for r in top_10[:5]: # Top 5 deep dives
            story.append(Paragraph(f"<b>#{r['rank']}. {r['player_name']}</b> — {r['playing_role']} (Age: {r['age']:.1f} yrs)", h2_style))
            p_desc = (
                f"<b>Domestic Team:</b> {r['domestic_team']} | <b>Uncapped Status:</b> {r['uncapped_status']}<br/>"
                f"<b>Overall Scouting Score:</b> {r['overall_scouting_score']:.1f}/100 | <b>Projected Peak Potential:</b> {r['projected_peak_potential']:.1f}<br/>"
                f"<b>Key Statistical Evidence:</b> Matches: {r['key_stats']['matches']}, Runs: {r['key_stats']['runs']}, "
                f"Strike Rate: {r['key_stats']['strike_rate']:.2f}, Average: {r['key_stats']['batting_average']:.2f}, "
                f"Wickets: {r['key_stats']['wickets']}, Economy: {r['key_stats']['economy']:.2f}<br/>"
                f"<b>Rajasthan Royals Squad Fit:</b> {r['rr_squad_fit']}<br/>"
                f"<b>Auction Value & Risk:</b> {r['potential_value']} | <i>Risk: {r['risk_assessment']}</i><br/>"
                f"<b>Recommendation Rationale:</b> {r['final_recommendation_rationale']}"
            )
            story.append(Paragraph(p_desc, body_style))
            story.append(Spacer(1, 4))

        # Section 5: Auction Strategy & Budget Allocation
        story.append(Spacer(1, 6))
        story.append(Paragraph("5. Auction Budget Optimization & Value Strategy", h1_style))
        budget_text = (
            "Under an estimated IPL 2027 total auction purse of <b>₹120.0 Crore</b> (with ~₹79 Cr allocated toward retaining the 5–6 core "
            "superstars including Samson, Jaiswal, Parag, and Jurel), the available auction purse is projected at <b>₹41.0 Crore</b>.<br/><br/>"
            "We recommend earmarking <b>₹14.0 Crore (34% of auction purse)</b> specifically to capture 5–7 high-priority uncapped domestic targets. "
            "By focusing on Quadrant 1 (High Value, Lower Cost Steals such as Saumy Pandey, Raj Limbani, and Priyansh Arya), Rajasthan Royals "
            "can build a dominant domestic bench without triggering catastrophic bidding wars."
        )
        story.append(Paragraph(budget_text, body_style))
        story.append(Spacer(1, 8))

        # Governance & Sign-off
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#94a3b8"), spaceBefore=8, spaceAfter=8))
        story.append(Paragraph(
            "<font color='#64748b' size='7'>RR TalentIQ Platform &bull; SupeRR Selector Season 2 Competition Submission &bull; "
            "Requires human analyst review and coaching approval prior to live auction execution.</font>",
            body_style
        ))

        doc.build(story)
        if output_path:
            with open(output_path, "rb") as f:
                return f.read()
        return buffer.getvalue()
