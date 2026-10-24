"""
IPL Analytics Pro - Team Analysis Page
Franchise performance rankings, head-to-head match-up simulator, and tactical win equity splits.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Team Analysis | IPL Analytics Pro", page_icon="🛡️", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.charts import (
    plot_team_wins,
    plot_head_to_head_summary,
    plot_team_score_distribution,
    style_fig
)
from analytics.data_loader import load_matches_data, load_deliveries_data
from analytics.team_analysis import TeamAnalytics

require_auth()
render_sidebar()

matches_df = load_matches_data()
deliveries_df = load_deliveries_data()
ta = TeamAnalytics(matches_df, deliveries_df)

st.markdown("""
<div class="main-header">
    <div>
        <h1>Franchise & Team Analytics</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            All-time win rates, historical trajectories, head-to-head simulations, and tactical equity splits
        </div>
    </div>
    <div>
        <span class="badge">FRANCHISE INTELLIGENCE</span>
    </div>
</div>
""", unsafe_allow_html=True)

team_summary = ta.get_all_teams_summary()

# Top Team Win Rates Table & Chart
col1, col2 = st.columns([1.1, 0.9])
with col1:
    st.plotly_chart(plot_team_wins(team_summary), use_container_width=True)
with col2:
    fig_win_pct = px.bar(
        team_summary.head(10).sort_values("Win %", ascending=True),
        x="Win %",
        y="Team",
        orientation="h",
        text="Win %",
        color="Win %",
        color_continuous_scale="Purples"
    )
    fig_win_pct.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(style_fig(fig_win_pct, "Top 10 Win Percentages (All Time)"), use_container_width=True)

# Comprehensive Leaderboard Table
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🏆 All-Time Franchise Performance Leaderboard</div>', unsafe_allow_html=True)
st.dataframe(team_summary, use_container_width=True, hide_index=True)

csv_team = team_summary.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Download Franchise Summary (CSV)",
    data=csv_team,
    file_name="ipl_franchise_leaderboard.csv",
    mime="text/csv"
)
st.markdown('</div>', unsafe_allow_html=True)

# Head-to-Head Simulator
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚔️ Interactive Head-to-Head Simulator</div>', unsafe_allow_html=True)

teams_list = ta.get_teams_list()
col_t1, col_t2 = st.columns(2)

with col_t1:
    idx_mi = teams_list.index("Mumbai Indians") if "Mumbai Indians" in teams_list else 0
    team1 = st.selectbox("Select Primary Team:", options=teams_list, index=idx_mi, key="h2h_team1")
with col_t2:
    idx_csk = teams_list.index("Chennai Super Kings") if "Chennai Super Kings" in teams_list else 1
    team2 = st.selectbox("Select Opponent Team:", options=teams_list, index=idx_csk, key="h2h_team2")

if team1 == team2:
    st.info("Please select two distinct franchises to simulate head-to-head match-up.")
else:
    h2h = ta.get_head_to_head(team1, team2)
    
    # H2H Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(f"Total Matches", h2h["total_played"])
    with c2:
        st.metric(f"{team1} Wins", f"{h2h['team1_wins']} ({h2h['team1_win_pct']}%)")
    with c3:
        st.metric(f"{team2} Wins", f"{h2h['team2_wins']} ({h2h['team2_win_pct']}%)")
    with c4:
        st.metric("Avg Scores (T1 vs T2)", f"{h2h['team1_avg_score']} vs {h2h['team2_avg_score']}")
        
    st.plotly_chart(plot_head_to_head_summary(h2h), use_container_width=True)
    
    st.markdown("<b>Historical Encounters Log:</b>", unsafe_allow_html=True)
    st.dataframe(h2h["matches_list"], use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# Team Season-by-Season Breakdown
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📅 Single Team Season Trajectory</div>', unsafe_allow_html=True)

inspect_team = st.selectbox("Select Team to Inspect:", options=teams_list, index=idx_csk, key="inspect_team")
season_breakdown = ta.get_team_season_breakdown(inspect_team)

if len(season_breakdown) > 0:
    fig_team_s = px.bar(
        season_breakdown,
        x="Season",
        y="Won",
        text="Won",
        color="Win %",
        color_continuous_scale="Teal",
        labels={"Won": "Matches Won", "Season": "Season"}
    )
    fig_team_s.update_traces(textposition="outside")
    st.plotly_chart(style_fig(fig_team_s, f"{inspect_team} Wins by Season"), use_container_width=True)
    st.dataframe(season_breakdown, use_container_width=True, hide_index=True)
else:
    st.info("No season records found for selected franchise.")
st.markdown('</div>', unsafe_allow_html=True)

# Team Score Distribution Box Plot
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📦 Innings Score Distributions</div>', unsafe_allow_html=True)
st.plotly_chart(plot_team_score_distribution(matches_df), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
