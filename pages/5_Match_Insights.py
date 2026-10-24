"""
IPL Analytics Pro - Match Insights Page
Historical records, record-breaking innings totals, closest finishes, and legendary performances.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Match Insights | IPL Analytics Pro", page_icon="⚡", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.charts import style_fig
from analytics.data_loader import load_matches_data, load_deliveries_data
from analytics.match_insights import MatchInsights

require_auth()
render_sidebar()

matches_df = load_matches_data()
deliveries_df = load_deliveries_data()
mi = MatchInsights(matches_df, deliveries_df)

st.markdown("""
<div class="main-header">
    <div>
        <h1>Match Insights & Record Books</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Record aggregate encounters, historic batting masterclasses, spellbinding bowling figures, and thrilling finishes
        </div>
    </div>
    <div>
        <span class="badge">HISTORICAL RECORD ARCHIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_agg, tab_inn, tab_thrill, tab_margins, tab_ind = st.tabs([
    "🔥 Highest Scoring Matches",
    "🚀 Record Innings Totals",
    "⏱️ Closest Finishes & Thrillers",
    "🏆 Largest Victory Margins",
    "🌟 Individual All-Time Masteries"
])

# Tab 1: Highest Match Aggregates
with tab_agg:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔥 Highest Combined Match Aggregates in IPL History</div>', unsafe_allow_html=True)
    high_matches = mi.get_highest_scoring_matches(10)
    
    fig_agg = px.bar(
        high_matches,
        x="total_match_runs",
        y=high_matches.apply(lambda r: f"{r['team1']} vs {r['team2']} ({r['season']})", axis=1),
        orientation="h",
        text="total_match_runs",
        color="total_match_runs",
        color_continuous_scale="Plasma",
        labels={"y": "Fixture", "total_match_runs": "Total Combined Runs"}
    )
    fig_agg.update_traces(textposition="outside")
    st.plotly_chart(style_fig(fig_agg, "Top 10 Highest Aggregate Run Encounters"), use_container_width=True)
    
    st.dataframe(high_matches, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Record Innings Totals
with tab_inn:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Highest Team Innings Totals (All Time)</div>', unsafe_allow_html=True)
    top_inn = mi.get_highest_innings_totals(12)
    
    fig_inn = px.bar(
        top_inn,
        x="Score",
        y="batting_team",
        orientation="h",
        text="Match_Score",
        color="Score",
        color_continuous_scale="Viridis",
        labels={"Score": "Total Runs", "batting_team": "Batting Team"}
    )
    fig_inn.update_traces(textposition="outside")
    st.plotly_chart(style_fig(fig_inn, "Highest Team Scores in IPL History"), use_container_width=True)
    
    st.dataframe(top_inn, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Closest Finishes & Thrillers
with tab_thrill:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⏱️ 1-Run Victories, 1-Wicket Thrillers & Super Overs</div>', unsafe_allow_html=True)
    closest = mi.get_closest_finishes(20)
    st.dataframe(closest, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 4: Largest Victory Margins
with tab_margins:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏆 Largest Margins of Victory by Runs</div>', unsafe_allow_html=True)
    top_runs_win = mi.get_largest_margins_by_runs(10)
    st.dataframe(top_runs_win, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 5: Individual Record Mastery
with tab_ind:
    col_ind_a, col_ind_b = st.columns(2)
    
    with col_ind_a:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏏 Highest Individual Batting Innings</div>', unsafe_allow_html=True)
        top_bat_ind = mi.get_highest_individual_scores(10)
        st.dataframe(top_bat_ind, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_ind_b:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 Best Bowling Figures in an Innings</div>', unsafe_allow_html=True)
        top_bowl_ind = mi.get_best_bowling_figures(10)
        st.dataframe(top_bowl_ind, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
