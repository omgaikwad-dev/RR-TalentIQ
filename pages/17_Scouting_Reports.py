"""
RR TalentIQ - Scouting Reports & Strategy Exports
Generates publication-grade PDF Executive Briefs and 16-Slide PowerPoint
presentation decks for Rajasthan Royals SupeRR Selector Season 2 competition submission.
"""

import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Scouting Reports | RR TalentIQ", page_icon="📄", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.player_ranker import PlayerRanker
from scouting.recommendations import RecommendationEngine
from reports.executive_summary import ExecutiveSummaryPDFGenerator
from reports.presentation_export import PresentationDeckGenerator

require_auth()
render_sidebar()

# Load Data & Generate Top 10
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)
rec_engine = RecommendationEngine(ranker)
top_10 = rec_engine.generate_top_10_recommendations(scored_df)

st.markdown("""
<div class="main-header">
    <div>
        <h1>Strategy Reports & Deliverables Export</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            One-click generation of PDF Strategy Dossiers and 16-Slide PowerPoint presentation decks
        </div>
    </div>
    <div>
        <span class="rr-badge">SUPERR SELECTOR S2 DELIVERABLES</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Export Actions Cards
col_pdf, col_pptx, col_data = st.columns(3)

with col_pdf:
    st.markdown("""
    <div class="scouting-card" style="text-align: center;">
        <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">📑</div>
        <h3 style="color: #ffffff; margin: 0.2rem 0;">Executive PDF Dossier</h3>
        <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.4;">
            Audit-grade multi-page strategy brief containing methodology, data provenance, Top 10 player dossiers, and auction allocations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Compiling ReportLab PDF..."):
        pdf_bytes = ExecutiveSummaryPDFGenerator.generate_pdf(top_10=top_10)
        st.download_button(
            label="📥 Download Strategy Dossier (PDF)",
            data=pdf_bytes,
            file_name="RR_TalentIQ_SupeRR_Selector_Strategy_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

with col_pptx:
    st.markdown("""
    <div class="scouting-card" style="text-align: center;">
        <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">📊</div>
        <h3 style="color: #ffffff; margin: 0.2rem 0;">16-Slide PPTX Deck</h3>
        <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.4;">
            Widescreen 16:9 presentation deck styled in Rajasthan Royals dark navy and pink, ready for direct competition submission.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Generating PowerPoint Deck..."):
        pptx_bytes = PresentationDeckGenerator.generate_presentation_deck(top_10=top_10)
        st.download_button(
            label="📥 Download Presentation Deck (PPTX)",
            data=pptx_bytes,
            file_name="RR_TalentIQ_SupeRR_Selector_Strategy_Deck.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
            type="primary"
        )

with col_data:
    st.markdown("""
    <div class="scouting-card" style="text-align: center;">
        <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">📈</div>
        <h3 style="color: #ffffff; margin: 0.2rem 0;">Audited Dataset Export</h3>
        <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.4;">
            Export the complete standardized domestic player database with 36+ metrics, scores, and eligibility audit tags.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    csv_bytes = scored_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Database (CSV)",
        data=csv_bytes,
        file_name="RR_TalentIQ_Domestic_Scouting_Database.csv",
        mime="text/csv",
        use_container_width=True
    )

st.write("")

# Detailed Interactive Preview of the Top 10 Shortlist
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">👑 Official Top 10 Recommendation Shortlist (Audited Profiles)</div>', unsafe_allow_html=True)

for r in top_10:
    with st.expander(f"#{r['rank']}. {r['player_name']} — {r['playing_role']} (Age: {r['age']:.1f} yrs | Scout Score: {r['overall_scouting_score']:.1f})"):
        c1, c2 = st.columns([1.1, 0.9])
        with c1:
            st.markdown(f"**State Team:** `{r['domestic_team']}` | **Eligibility:** `{r['uncapped_status']}`")
            st.markdown(f"**Peak Projected Ceiling:** `{r['projected_peak_potential']:.1f}` | **Consistency Score:** `{r['consistency_score']:.1f}`")
            st.markdown(f"**Key Statistical Proof:** Matches: `{r['key_stats']['matches']}`, Runs: `{r['key_stats']['runs']}`, SR: `{r['key_stats']['strike_rate']:.2f}`, Wickets: `{r['key_stats']['wickets']}`, Economy: `{r['key_stats']['economy']:.2f}`")
            st.markdown(f"**Rajasthan Royals Squad Fit:** {r['rr_squad_fit']}")
            st.markdown(f"**Recommendation Rationale:** {r['final_recommendation_rationale']}")
        with c2:
            st.markdown(f"**Estimated Auction Valuation:** <span style='color: #2ecc71; font-weight: 700;'>{r['potential_value']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Risk Profile:** `{r['risk_assessment']}`")
            st.markdown("**Key Assets:**")
            for s in r["strengths"]:
                st.markdown(f"<div style='font-size: 0.8rem; color: #cbd5e1;'>✔️ {s}</div>", unsafe_allow_html=True)
            st.markdown("**Development Watch:**")
            for w in r["weaknesses"]:
                st.markdown(f"<div style='font-size: 0.8rem; color: #cbd5e1;'>⚠️ {w}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

