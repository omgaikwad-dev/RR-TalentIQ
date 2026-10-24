"""
IPL Analytics Pro - Venue Analysis Page
Stadium dynamics, average scores, toss & chasing equity, and stadium historical records.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Venue Analysis | IPL Analytics Pro", page_icon="🏟️", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.charts import plot_venue_matches, style_fig
from analytics.data_loader import load_matches_data, load_deliveries_data
from analytics.venue_analysis import VenueAnalytics

require_auth()
render_sidebar()

matches_df = load_matches_data()
deliveries_df = load_deliveries_data()
va = VenueAnalytics(matches_df, deliveries_df)

st.markdown("""
<div class="main-header">
    <div>
        <h1>Stadium & Venue Analytics</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Pitch characteristics, average par scores, defending vs chasing win bias, and stadium records
        </div>
    </div>
    <div>
        <span class="badge">STADIUM INTELLIGENCE</span>
    </div>
</div>
""", unsafe_allow_html=True)

venues_summary = va.get_venues_summary(min_matches=5)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_venue_matches(venues_summary), use_container_width=True)
with col2:
    # 1st Innings vs 2nd Innings Par Score Comparison
    top_10_v = venues_summary.head(10)
    fig_scores = px.bar(
        top_10_v,
        x="Venue",
        y=["Avg 1st Inn Score", "Avg 2nd Inn Score"],
        barmode="group",
        color_discrete_sequence=["#FFB703", "#48CAE4"]
    )
    st.plotly_chart(style_fig(fig_scores, "Par Scores: 1st Innings vs 2nd Innings (Top 10 Stadiums)"), use_container_width=True)

# Defending vs Chasing Win Bias by Stadium
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚖️ Defending vs Chasing Equity by Stadium</div>', unsafe_allow_html=True)

fig_bias = px.bar(
    top_10_v,
    x="Venue",
    y=["Bat 1st Win %", "Chase Win %"],
    barmode="stack",
    color_discrete_sequence=["#06D6A0", "#EF476F"],
    labels={"value": "Win Percentage (%)", "variable": "Tactical Choice"}
)
st.plotly_chart(style_fig(fig_bias, "Defending vs Chasing Win Equity Breakdown"), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Interactive Stadium Deep Dive
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 Individual Stadium Deep Dive</div>', unsafe_allow_html=True)

venues_list = va.get_venues_list()
selected_venue = st.selectbox("Select Stadium to Inspect:", options=venues_list, index=0)
v_details = va.get_venue_details(selected_venue)

vc1, vc2, vc3, vc4 = st.columns(4)
with vc1:
    st.metric("Total Matches Hosted", v_details["total_matches"])
with vc2:
    st.metric("Total Runs Scored", f"{v_details['total_runs']:,}")
with vc3:
    st.metric("Total Wickets Taken", f"{v_details['total_wickets']:,}")
with vc4:
    st.metric("Total Sixes Struck", f"{v_details['total_sixes']:,}")

st.write("")
st.markdown(f"<b>Most Dominant Franchise:</b> <span style='color: #ffb703; font-weight: 700;'>{v_details['top_team']}</span> ({v_details['top_team_wins']} Wins)", unsafe_allow_html=True)

st.markdown("<b>Highest Match Scores at this Stadium:</b>", unsafe_allow_html=True)
st.dataframe(v_details["highest_matches"], use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# Comprehensive Venues Table & CSV Export
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Comprehensive Stadium Metrics Master Table</div>', unsafe_allow_html=True)
st.dataframe(venues_summary, use_container_width=True, hide_index=True)

csv_venues = venues_summary.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Download Venue Analytics Master Table (CSV)",
    data=csv_venues,
    file_name="ipl_venue_analytics.csv",
    mime="text/csv"
)
st.markdown('</div>', unsafe_allow_html=True)
