"""
RR TalentIQ - Bowling Scouting & Containment Analytics
Advanced bowling analytics, economy rate suppression,
strike rate potency, and dot-ball dominance across domestic bowlers.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bowling Scouting | RR TalentIQ", page_icon="🎯", layout="wide")

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
from analytics.bowling_scouting import BowlingScoutingEngine
from scouting.player_ranker import PlayerRanker

require_auth()
render_sidebar()

# Load Data
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)
bowl_engine = BowlingScoutingEngine()
bowl_df = bowl_engine.calculate_bowling_metrics(scored_df)

render_rr_brand_header(
    page_title="Domestic Bowling Intelligence",
    subtitle="Bowling Impact Index (BII), economy containment, strike rate efficiency, and dot-ball mastery",
    badge_text="CONTAINMENT & WICKETS"
)

# Interactive Filters Bar
with st.container():
    st.markdown('<div class="rr-filter-panel">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        min_overs = st.slider("Minimum Overs Bowled:", min_value=4.0, max_value=60.0, value=10.0, step=2.0)
    with c2:
        styles_list = ["All Styles"] + sorted(bowl_df["bowling_style"].dropna().unique().tolist())
        sel_style = st.selectbox("Bowling Style Filter:", options=styles_list)
    with c3:
        max_age_bowl = st.slider("Max Age Limit:", min_value=18.0, max_value=32.0, value=25.0, step=0.5)
    st.markdown('</div>', unsafe_allow_html=True)

qual_bowlers = bowl_df[(bowl_df["overs"] >= min_overs) & (bowl_df["age"] <= max_age_bowl)].copy()
if sel_style != "All Styles":
    qual_bowlers = qual_bowlers[qual_bowlers["bowling_style"] == sel_style]

# Visual Row 1: Economy vs Bowling Strike Rate
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ Bowling Efficiency Frontier (Economy vs Strike Rate)</div>', unsafe_allow_html=True)
    
    fig_econ_sr = px.scatter(
        qual_bowlers,
        x="economy",
        y="bowling_strike_rate",
        size="wickets",
        color="bowling_style",
        hover_name="player_name",
        hover_data={"age": True, "overs": True, "wickets": True, "bowling_average": ":.1f", "dot_ball_pct_bowl": ":.1f"},
        labels={"economy": "Economy Rate (Lower is Better)", "bowling_strike_rate": "Balls Per Wicket (Lower is Better)"},
        color_discrete_sequence=["#00e5ff", "#ea1a85", "#ffd166", "#00e676", "#ff5252"]
    )
    fig_econ_sr.add_vline(x=7.50, line_dash="dash", line_color="rgba(0, 229, 255, 0.4)")
    fig_econ_sr.add_hline(y=16.0, line_dash="dash", line_color="rgba(234, 26, 133, 0.4)")
    fig_econ_sr = style_scouting_fig(fig_econ_sr)
    fig_econ_sr.update_layout(height=420)
    st.plotly_chart(fig_econ_sr, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛑 Dot-Ball Pressure vs Wickets</div>', unsafe_allow_html=True)
    
    fig_dots = px.scatter(
        qual_bowlers,
        x="dot_ball_pct_bowl",
        y="wickets",
        size="bowling_impact_index",
        color="bowling_style",
        hover_name="player_name",
        hover_data={"economy": ":.2f", "overs": True, "age": True},
        labels={"dot_ball_pct_bowl": "Dot Ball % Bowled (Higher is Better)", "wickets": "Total Wickets"},
        color_discrete_sequence=["#00e5ff", "#ea1a85", "#ffd166", "#00e676", "#ff5252"]
    )
    fig_dots = style_scouting_fig(fig_dots)
    fig_dots.update_layout(height=420)
    st.plotly_chart(fig_dots, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Top Bowling Impact Index Leaderboard
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🏆 Top Bowling Impact Index (BII) Rankings</div>', unsafe_allow_html=True)

top_bii = qual_bowlers.sort_values(by="bowling_impact_index", ascending=False).reset_index(drop=True)
top_bii.index = top_bii.index + 1

bowl_cols = [
    "player_name", "playing_role", "bowling_style", "age",
    "bowling_impact_index", "economy", "bowling_strike_rate", "bowling_average",
    "wickets", "overs", "dot_ball_pct_bowl", "estimated_dot_balls"
]
st.dataframe(top_bii[bowl_cols], use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
