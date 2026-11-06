"""
RR TalentIQ - Batting Scouting & Boundary Dominance
Advanced batting analytics, strike rate vs average frontiers,
dot-ball suppression, and non-boundary strike rotation efficiency.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Batting Scouting | RR TalentIQ", page_icon="🏏", layout="wide")

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
from analytics.batting_scouting import BattingScoutingEngine
from scouting.player_ranker import PlayerRanker

require_auth()
render_sidebar()

# Load Data
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)
bat_engine = BattingScoutingEngine()
bat_df = bat_engine.calculate_batting_metrics(scored_df)

# Header
st.markdown("""
<div class="main-header">
    <div>
        <h1>Domestic Batting Intelligence</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Batting Impact Index (BII), strike efficiency frontiers, boundary volume, and dot-ball control
        </div>
    </div>
    <div>
        <span class="rr-badge">POWER & ROTATION SCOUTING</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Batters Filter
min_balls = st.slider("Minimum Balls Faced Filter:", min_value=10, max_value=300, value=60, step=10)
qual_batters = bat_df[bat_df["balls_faced"] >= min_balls].copy()

# Visual Row 1: Strike Rate vs Average Scatter & Boundary Rate vs Dot Ball %
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎯 T20 Batting Frontier: Strike Rate vs Average</div>', unsafe_allow_html=True)
    
    fig_scatter = px.scatter(
        qual_batters,
        x="strike_rate",
        y="batting_average",
        size="runs",
        color="playing_role",
        hover_name="player_name",
        hover_data={"age": True, "boundary_pct_bat": ":.1f", "dot_ball_pct_bat": ":.1f", "balls_faced": True},
        color_discrete_sequence=["#ff2a85", "#00b4d8", "#ffb703", "#2ec4b6", "#e76f51"],
        labels={"strike_rate": "Strike Rate (T20)", "batting_average": "Batting Average", "playing_role": "Role"}
    )
    # Add benchmark crosshairs at 140 SR, 30 Avg
    fig_scatter.add_vline(x=140.0, line_dash="dash", line_color="rgba(255,255,255,0.25)")
    fig_scatter.add_hline(y=30.0, line_dash="dash", line_color="rgba(255,255,255,0.25)")
    fig_scatter = style_scouting_fig(fig_scatter)
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💥 Boundary Dominance vs Dot Ball %</div>', unsafe_allow_html=True)
    
    fig_dots = px.scatter(
        qual_batters,
        x="dot_ball_pct_bat",
        y="boundary_pct_bat",
        size="strike_rate",
        color="playing_role",
        hover_name="player_name",
        hover_data={"runs": True, "strike_rate": ":.1f", "fours": True, "sixes": True},
        color_discrete_sequence=["#ff2a85", "#00b4d8", "#ffb703", "#2ec4b6", "#e76f51"],
        labels={"dot_ball_pct_bat": "Dot Ball % (Lower is Better)", "boundary_pct_bat": "Boundary Run % (Higher is Better)"}
    )
    fig_dots = style_scouting_fig(fig_dots)
    fig_dots.update_layout(height=400)
    st.plotly_chart(fig_dots, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Top Batting Impact Index Leaderboard
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🏆 Top Batting Impact Index (BII) Rankings</div>', unsafe_allow_html=True)

top_bii = qual_batters.sort_values(by="batting_impact_index", ascending=False).reset_index(drop=True)
top_bii.index = top_bii.index + 1

b_cols = [
    "player_name", "playing_role", "age", "batting_impact_index",
    "strike_rate", "batting_average", "runs", "balls_faced",
    "boundary_pct_bat", "rotation_strike_rate", "dot_ball_pct_bat", "fifties", "hundreds"
]
st.dataframe(top_bii[b_cols], use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

