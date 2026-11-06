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
from components.scouting_components import style_scouting_fig
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

# Header
st.markdown("""
<div class="main-header">
    <div>
        <h1>All-Rounders & Wicketkeeper Evaluation</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Harmonic dual-discipline gating, balance ratios, and glovework indexing for specialized multi-skilled roles
        </div>
    </div>
    <div>
        <span class="rr-badge">DUAL-DISCIPLINE INTELLIGENCE</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_ar, tab_wk = st.tabs(["⚖️ All-Rounder Evaluation", "🧤 Wicketkeeper-Batter Evaluation"])

with tab_ar:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Batting Impact vs Bowling Impact (All-Rounder Balance Frontier)</div>', unsafe_allow_html=True)
    
    # Filter to players with at least some batting and bowling activity
    ar_pool = ar_df[(ar_df["balls_faced"] >= 30) | (ar_df["overs"] >= 5.0)].copy()
    
    fig_ar = px.scatter(
        ar_pool,
        x="batting_impact_index",
        y="bowling_impact_index",
        size="allrounder_composite_score",
        color="allrounder_archetype",
        hover_name="player_name",
        hover_data={"age": True, "strike_rate": ":.1f", "economy": ":.2f", "wickets": True, "runs": True, "discipline_balance_ratio": ":.2f"},
        labels={
            "batting_impact_index": "Batting Impact Index (BII)",
            "bowling_impact_index": "Bowling Impact Index (BII)",
            "allrounder_archetype": "Archetype"
        },
        color_discrete_sequence=["#ff2a85", "#00b4d8", "#2ec4b6", "#ffb703"]
    )
    # 45-degree parity line
    fig_ar.add_shape(type="line", x0=0, y0=0, x1=90, y1=90, line=dict(color="rgba(255,255,255,0.2)", dash="dash"))
    fig_ar = style_scouting_fig(fig_ar)
    fig_ar.update_layout(height=420)
    st.plotly_chart(fig_ar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Leaderboard of All-Rounders
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏆 All-Rounder Composite Score Leaderboard (Harmonic Gating)</div>', unsafe_allow_html=True)
    
    top_ar = ar_pool.sort_values(by="allrounder_composite_score", ascending=False).reset_index(drop=True)
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
    st.markdown('<div class="section-title">🧤 Wicketkeeper-Batter Evaluation Matrix</div>', unsafe_allow_html=True)
    
    # Filter to designated keepers or those with catches/stumpings
    wk_candidates = wk_df[
        (wk_df["playing_role"] == "Wicketkeeper-Batter") | 
        (wk_df["stumpings"] >= 1) | 
        (wk_df["catches"] >= 10)
    ].sort_values(by="wicketkeeper_composite_score", ascending=False).reset_index(drop=True)
    wk_candidates.index = wk_candidates.index + 1

    wk_cols = [
        "player_name", "age", "wicketkeeper_composite_score",
        "keeping_impact_index", "batting_impact_index",
        "strike_rate", "batting_average", "runs",
        "catches", "stumpings", "total_dismissals", "dismissals_per_match", "stumping_ratio"
    ]
    st.dataframe(wk_candidates[wk_cols], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

