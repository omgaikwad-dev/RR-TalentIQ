"""
RR TalentIQ - Player Explorer & 360-Degree Dossier
Interactive player search, multi-metric filtering, radar profiling,
and individual scout evaluations across the domestic talent pool.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Player Explorer | RR TalentIQ", page_icon="🔍", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.scouting_components import plot_scouting_radar, render_player_spotlight_card
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.player_ranker import PlayerRanker
from scouting.player_profiles import PlayerProfileEngine

require_auth()
render_sidebar()

# Load Data
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)

st.markdown("""
<div class="main-header">
    <div>
        <h1>Player Explorer & Talent Dossier</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Deep multi-dimensional profile exploration, 7-axis radar diagrams, and tactical strengths/weaknesses
        </div>
    </div>
    <div>
        <span class="rr-badge">360° TALENT INTELLIGENCE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Search & Filters Bar
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
    
    with c1:
        search_query = st.text_input("🔍 Search Player by Name:", placeholder="e.g. Priyansh, Rizvi, Limbani...")
    with c2:
        roles_list = ["All Roles"] + sorted(scored_df["playing_role"].unique().tolist())
        selected_role = st.selectbox("Filter by Role:", options=roles_list)
    with c3:
        max_age_val = st.slider("Max Age Threshold:", min_value=19.0, max_value=36.0, value=25.0, step=0.5)
    with c4:
        min_matches = st.number_input("Min Matches Played:", min_value=1, max_value=50, value=5)

    st.markdown('</div>', unsafe_allow_html=True)

# Apply Filters
filtered_df = scored_df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df["player_name"].str.contains(search_query, case=False, na=False)]
if selected_role != "All Roles":
    filtered_df = filtered_df[filtered_df["playing_role"] == selected_role]
filtered_df = filtered_df[(filtered_df["age"].notnull()) & (filtered_df["age"] <= max_age_val)]
filtered_df = filtered_df[filtered_df["matches"] >= min_matches]

st.markdown(f"""
<div style="color: #48cae4; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.8rem;">
    📊 Displaying <b>{len(filtered_df)}</b> domestic candidates matching current criteria
</div>
""", unsafe_allow_html=True)

if len(filtered_df) == 0:
    st.warning("⚠️ No players match the specified filters. Please loosen the age threshold or clear your search.")
else:
    # Top Section: Selected Player Deep Dive Dossier
    selected_player_name = st.selectbox(
        "Select Player to Inspect 360° Dossier & Radar:",
        options=filtered_df["player_name"].tolist(),
        index=0
    )
    
    selected_row = filtered_df[filtered_df["player_name"] == selected_player_name].iloc[0]
    dossier = PlayerProfileEngine.generate_player_dossier(selected_row)
    
    col_dossier_l, col_dossier_r = st.columns([1.2, 0.8])
    
    with col_dossier_l:
        render_player_spotlight_card(dossier)
        
        # Strengths & Weaknesses
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚡ Algorithmic Strengths & Vulnerabilities</div>', unsafe_allow_html=True)
        
        c_str, c_wk = st.columns(2)
        with c_str:
            st.markdown("<b style='color: #2ecc71;'>Key Strengths:</b>", unsafe_allow_html=True)
            for s in dossier["strengths"]:
                st.markdown(f"<div style='font-size: 0.83rem; margin-bottom: 0.35rem; color: #cbd5e1;'>✔️ {s}</div>", unsafe_allow_html=True)
        with c_wk:
            st.markdown("<b style='color: #e74c3c;'>Areas for Development:</b>", unsafe_allow_html=True)
            for w in dossier["weaknesses"]:
                st.markdown(f"<div style='font-size: 0.83rem; margin-bottom: 0.35rem; color: #cbd5e1;'>⚠️ {w}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_dossier_r:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🕸️ 7-Axis Skill Radar</div>', unsafe_allow_html=True)
        radar_fig = plot_scouting_radar(selected_player_name, dossier["radar_dimensions"])
        st.plotly_chart(radar_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Master Table of Filtered Players
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Domestic Candidate Performance Table</div>', unsafe_allow_html=True)
    
    display_cols = [
        "player_name", "playing_role", "age", "domestic_team",
        "overall_scouting_score", "projected_peak_potential", "strike_rate",
        "batting_average", "boundary_pct_bat", "economy", "bowling_strike_rate",
        "wickets", "matches"
    ]
    st.dataframe(
        filtered_df[display_cols].sort_values("overall_scouting_score", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    csv_bytes = filtered_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Candidate Records (CSV)",
        data=csv_bytes,
        file_name="rr_scouted_candidates.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)

