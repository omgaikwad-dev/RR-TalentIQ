"""
RR TalentIQ - Talent Rankings & Sensitivity Analysis
Multi-criteria decision leaderboard with interactive weight calibration
and automated sensitivity testing across distinct franchise strategies.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Talent Rankings | RR TalentIQ", page_icon="🏆", layout="wide")

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
from scouting.player_ranker import PlayerRanker

require_auth()
render_sidebar()

loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)

st.markdown("""
<div class="main-header">
    <div>
        <h1>Domestic Talent Rankings & Sensitivity Engine</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Transparent multi-criteria scoring leaderboard with live weight tuning and ranking stability testing
        </div>
    </div>
    <div>
        <span class="rr-badge">MCDA DECISION ENGINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_leaderboard, tab_sensitivity = st.tabs(["🏆 Interactive Leaderboard", "📈 Sensitivity Analysis"])

with tab_leaderboard:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎛️ Multi-Criteria Scoring Weight Calibration</div>', unsafe_allow_html=True)
    
    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
    with col_w1:
        w_perf = st.slider("Role Performance Weight:", min_value=0.10, max_value=0.70, value=0.45, step=0.05)
    with col_w2:
        w_pot = st.slider("Development Potential Weight:", min_value=0.05, max_value=0.50, value=0.25, step=0.05)
    with col_w3:
        w_cons = st.slider("Consistency Weight:", min_value=0.05, max_value=0.30, value=0.15, step=0.05)
    with col_w4:
        w_conf = st.slider("Sample Confidence Weight:", min_value=0.05, max_value=0.30, value=0.15, step=0.05)

    custom_weights = {
        "role_performance": w_perf,
        "development_potential": w_pot,
        "consistency": w_cons,
        "sample_confidence": w_conf
    }

    # Filter controls
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        roles_opt = ["All Roles"] + sorted(raw_df["playing_role"].unique().tolist())
        sel_role = st.selectbox("Filter Leaderboard by Role:", options=roles_opt)
    with c_f2:
        max_age_cap = st.slider("Maximum Age Limit:", min_value=19.0, max_value=35.0, value=26.0, step=0.5)

    st.markdown('</div>', unsafe_allow_html=True)

    # Compute custom rankings
    ranker = PlayerRanker(weights=custom_weights)
    ranked_df = ranker.rank_players(
        raw_df,
        role_filter=None if sel_role == "All Roles" else sel_role,
        max_age=max_age_cap
    )

    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">👑 Calibrated Leaderboard ({len(ranked_df)} Qualified Players)</div>', unsafe_allow_html=True)
    
    leader_cols = [
        "rank", "player_name", "playing_role", "age",
        "overall_scouting_score", "role_performance_score", "projected_peak_potential",
        "consistency_score", "domestic_team", "strike_rate", "economy", "matches"
    ]
    st.dataframe(ranked_df[leader_cols], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_sensitivity:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔬 Strategy Paradigm Sensitivity Testing</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 1rem; line-height: 1.6;">
        Tests rank movement across three distinct franchise strategy paradigms:
        <br>&bull; <b>Balanced (Recommended):</b> 45% Performance, 25% Potential, 15% Consistency, 15% Sample Conf
        <br>&bull; <b>High Potential (Youth Focus):</b> 30% Performance, 45% Potential, 15% Consistency, 10% Sample Conf
        <br>&bull; <b>Win-Now (Immediate Impact):</b> 60% Performance, 10% Potential, 20% Consistency, 10% Sample Conf
    </div>
    """, unsafe_allow_html=True)

    default_ranker = PlayerRanker()
    sens_df = default_ranker.run_sensitivity_analysis(raw_df)

    display_sens = [
        "player_name", "playing_role", "age",
        "rank_Balanced (Recommended)", "rank_High Potential (Youth Ceilings)", "rank_Win-Now (Immediate Impact)",
        "rank_range", "rank_stability"
    ]
    st.dataframe(sens_df[display_sens], use_container_width=True)

    # Rank Stability Distribution
    st.markdown('<div class="section-title" style="margin-top: 1rem;">📊 Ranking Stability Distribution</div>', unsafe_allow_html=True)
    fig_stab = px.histogram(
        sens_df,
        x="rank_stability",
        color="rank_stability",
        color_discrete_map={"Ultra Stable": "#2ecc71", "Moderately Stable": "#f39c12", "Sensitive to Weights": "#e74c3c"}
    )
    fig_stab = style_scouting_fig(fig_stab)
    fig_stab.update_layout(height=280, showlegend=False)
    st.plotly_chart(fig_stab, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

