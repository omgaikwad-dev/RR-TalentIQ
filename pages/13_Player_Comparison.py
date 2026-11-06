"""
RR TalentIQ - Player Comparison Engine
Enables head-to-head multi-player comparison for up to 4 domestic players
with dual radar overlays, side-by-side metric tables, and strengths/weaknesses.
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Player Comparison | RR TalentIQ", page_icon="⚖️", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.scouting_components import plot_scouting_radar
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
        <h1>Head-to-Head Player Comparison</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Compare up to 4 domestic prospects across 7 radar skill dimensions and empirical metrics
        </div>
    </div>
    <div>
        <span class="rr-badge">MULTI-CANDIDATE BENCHMARK</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Multiselect Player Selector (Up to 4 players)
all_player_names = scored_df["player_name"].tolist()
default_selection = [all_player_names[0], all_player_names[1]] if len(all_player_names) >= 2 else all_player_names

selected_players = st.multiselect(
    "Select 2 to 4 Players for Head-to-Head Comparison:",
    options=all_player_names,
    default=default_selection,
    max_selections=4
)

if len(selected_players) < 2:
    st.info("💡 Please select at least two players to generate comparative analytics.")
else:
    # Gather dossiers
    dossiers = []
    for p_name in selected_players:
        row = scored_df[scored_df["player_name"] == p_name].iloc[0]
        d = PlayerProfileEngine.generate_player_dossier(row)
        dossiers.append(d)

    # Top Row: Side-by-Side KPI Cards
    kpi_cols = st.columns(len(dossiers))
    for idx, d in enumerate(dossiers):
        with kpi_cols[idx]:
            st.markdown(f"""
            <div class="scouting-card">
                <div style="font-size: 0.75rem; color: #ff75a0; font-weight: 700;">{d['playing_role']}</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff; margin: 0.2rem 0;">{d['player_name']}</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Age: <b style="color: #ffffff;">{d['age']:.1f} yrs</b> | {d['domestic_team']}</div>
                <div style="margin: 0.6rem 0; background: rgba(255, 42, 133, 0.15); border: 1px solid #ff2a85; border-radius: 8px; padding: 0.4rem; text-align: center;">
                    <div style="font-size: 0.7rem; color: #cbd5e1; text-transform: uppercase;">Scouting Rating</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #ff2a85;">{d['overall_scouting_score']:.1f}</div>
                </div>
                <div style="font-size: 0.8rem; color: #cbd5e1;"><b>Peak Potential:</b> <span style="color: #48cae4;">{d['projected_peak_potential']:.1f}</span></div>
                <div style="font-size: 0.8rem; color: #cbd5e1;"><b>Consistency:</b> <span style="color: #ffb703;">{d['consistency_score']:.1f}</span></div>
            </div>
            """, unsafe_allow_html=True)

    # Middle Section: Radar Comparison Chart Overlay
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🕸️ Multi-Player 7-Axis Skill Radar Overlay</div>', unsafe_allow_html=True)
    
    categories = list(dossiers[0]["radar_dimensions"].keys())
    categories_closed = categories + [categories[0]]
    
    colors = ["#ff2a85", "#00b4d8", "#ffb703", "#2ec4b6"]
    
    fig_radar = go.Figure()
    for idx, d in enumerate(dossiers):
        vals = [d["radar_dimensions"][cat] for cat in categories]
        vals_closed = vals + [vals[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor=f"rgba({int(colors[idx][1:3], 16)}, {int(colors[idx][3:5], 16)}, {int(colors[idx][5:7], 16)}, 0.15)",
            line=dict(color=colors[idx], width=2.5),
            name=d["player_name"]
        ))
        
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255, 255, 255, 0.12)", tickfont=dict(color="#94a3b8", size=9)),
            angularaxis=dict(gridcolor="rgba(255, 255, 255, 0.12)", tickfont=dict(color="#ffffff", size=11)),
            bgcolor="rgba(20, 30, 55, 0.5)"
        ),
        paper_bgcolor="#0b132b",
        font=dict(color="#f8fafc"),
        height=450,
        margin=dict(l=40, r=40, t=30, b=30)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Side-by-Side Metric Comparison Table
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Direct Metric Breakdown</div>', unsafe_allow_html=True)
    
    comp_rows = [
        ("Playing Role", lambda d: d["playing_role"]),
        ("Age (Years on 2027-01-01)", lambda d: f"{d['age']:.1f}"),
        ("Overall Scouting Score", lambda d: f"{d['overall_scouting_score']:.1f}"),
        ("Projected Peak Potential", lambda d: f"{d['projected_peak_potential']:.1f}"),
        ("Consistency Score", lambda d: f"{d['consistency_score']:.1f}"),
        ("Matches Played", lambda d: str(d["matches"])),
        ("Total Runs", lambda d: str(d["runs"])),
        ("Strike Rate", lambda d: f"{d['strike_rate']:.2f}"),
        ("Batting Average", lambda d: f"{d['batting_average']:.2f}"),
        ("Total Wickets", lambda d: str(d["wickets"])),
        ("Economy Rate", lambda d: f"{d['economy']:.2f}"),
        ("Bowling Strike Rate", lambda d: f"{d['bowling_strike_rate']:.2f}"),
        ("Catches / Stumpings", lambda d: f"{d['catches']} / {d['stumpings']}")
    ]
    
    table_data = {"Metric": [r[0] for r in comp_rows]}
    for d in dossiers:
        table_data[d["player_name"]] = [r[1](d) for r in comp_rows]
        
    df_table = pd.DataFrame(table_data)
    st.table(df_table.set_index("Metric"))
    st.markdown('</div>', unsafe_allow_html=True)

