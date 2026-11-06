"""
RR TalentIQ - All-Rounder & Wicketkeeper Deep Dive
Independent two-way discipline evaluation for all-rounders
and integrated batting-plus-glovework analysis for wicketkeepers.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="All-Rounders & Keepers | RR TalentIQ", page_icon="⚖️", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.scouting_components import render_rr_brand_header, style_scouting_fig
from analytics.domestic_data_loader import DomesticDataLoader
from analytics.allrounder_scouting import DualDisciplineScoutingEngine
from scouting.player_ranker import PlayerRanker

require_auth()
render_sidebar()

# Load Data
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)
dual_engine = DualDisciplineScoutingEngine()
ar_df = dual_engine.evaluate_allrounders(scored_df)
wk_df = dual_engine.evaluate_wicketkeepers(scored_df)

render_rr_brand_header(
    page_title="All-Rounders & Wicketkeepers",
    subtitle="Harmonic dual-discipline gating, balance ratios, and glovework indexing for specialized multi-skilled roles",
    badge_text="DUAL DISCIPLINE SPECIALISTS"
)

tab_ar, tab_wk = st.tabs(["⚡ All-Rounder Balance & Impact", "🧤 Wicketkeeper-Batter Evaluation"])

with tab_ar:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Two-Way Contribution Matrix (Batting vs Bowling Index)</div>', unsafe_allow_html=True)
    
    fig_ar_matrix = px.scatter(
        ar_df,
        x="batting_impact_index",
        y="bowling_impact_index",
        size="allrounder_composite_score",
        color="allrounder_archetype",
        hover_name="player_name",
        hover_data={"age": True, "strike_rate": ":.1f", "economy": ":.2f", "wickets": True, "runs": True},
        color_discrete_sequence=["#ea1a85", "#00e5ff", "#ffd166", "#00e676", "#ff5252"],
        labels={"batting_impact_index": "Batting Impact Index (0-100)", "bowling_impact_index": "Bowling Impact Index (0-100)"}
    )
    # 50-50 Crosshair
    fig_ar_matrix.add_vline(x=50.0, line_dash="dash", line_color="rgba(234, 26, 133, 0.4)")
    fig_ar_matrix.add_hline(y=50.0, line_dash="dash", line_color="rgba(0, 229, 255, 0.4)")
    fig_ar_matrix = style_scouting_fig(fig_ar_matrix)
    fig_ar_matrix.update_layout(height=450)
    st.plotly_chart(fig_ar_matrix, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Leaderboard Table
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👑 Top All-Rounder Composite Score (ARCS) Leaderboard</div>', unsafe_allow_html=True)
    
    top_ar = ar_df.sort_values(by="allrounder_composite_score", ascending=False).reset_index(drop=True)
    top_ar.index = top_ar.index + 1
    
    ar_cols = [
        "player_name", "playing_role", "allrounder_archetype", "age",
        "allrounder_composite_score", "discipline_balance_ratio",
        "batting_impact_index", "bowling_impact_index",
        "runs", "strike_rate", "wickets", "economy"
    ]
    st.dataframe(top_ar[ar_cols], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_wk:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧤 Wicketkeeper Composite Score (WCS) Leaderboard</div>', unsafe_allow_html=True)
    
    top_wk = wk_df.sort_values(by="wicketkeeper_composite_score", ascending=False).reset_index(drop=True)
    top_wk.index = top_wk.index + 1
    
    wk_cols = [
        "player_name", "playing_role", "age", "wicketkeeper_composite_score",
        "batting_impact_index", "runs", "strike_rate", "batting_average",
        "catches", "stumpings", "total_dismissals"
    ]
    st.dataframe(top_wk[wk_cols], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
