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
from components.scouting_components import render_rr_brand_header, style_scouting_fig
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

render_rr_brand_header(
    page_title="Domestic Batting Intelligence",
    subtitle="Batting Impact Index (BII), strike efficiency frontiers, boundary volume, and dot-ball control",
    badge_text="POWER & ROTATION SCOUTING"
)

# Interactive Batters Filter Bar
with st.container():
    st.markdown('<div class="rr-filter-panel">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        min_balls = st.slider("Minimum Balls Faced Threshold:", min_value=10, max_value=300, value=60, step=10)
    with c2:
        roles_avail = ["All Batting Roles"] + sorted(bat_df["playing_role"].unique().tolist())
        sel_role = st.selectbox("Batting Role Filter:", options=roles_avail)
    with c3:
        max_age_bat = st.slider("Max Age Limit:", min_value=18.0, max_value=32.0, value=25.0, step=0.5)
    st.markdown('</div>', unsafe_allow_html=True)

qual_batters = bat_df[(bat_df["balls_faced"] >= min_balls) & (bat_df["age"] <= max_age_bat)].copy()
if sel_role != "All Batting Roles":
    qual_batters = qual_batters[qual_batters["playing_role"] == sel_role]

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
        color_discrete_sequence=["#ea1a85", "#00e5ff", "#ffd166", "#00e676", "#ff5252"],
        labels={"strike_rate": "Strike Rate (T20)", "batting_average": "Batting Average", "playing_role": "Role"}
    )
    fig_scatter.add_vline(x=140.0, line_dash="dash", line_color="rgba(234, 26, 133, 0.4)")
    fig_scatter.add_hline(y=30.0, line_dash="dash", line_color="rgba(0, 229, 255, 0.4)")
    fig_scatter = style_scouting_fig(fig_scatter)
    fig_scatter.update_layout(height=420)
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
        color_discrete_sequence=["#ea1a85", "#00e5ff", "#ffd166", "#00e676", "#ff5252"],
        labels={"dot_ball_pct_bat": "Dot Ball % (Lower is Better)", "boundary_pct_bat": "Boundary Run % (Higher is Better)"}
    )
    fig_dots = style_scouting_fig(fig_dots)
    fig_dots.update_layout(height=420)
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
