"""
RR TalentIQ - Scouting Overview & Mission Control
Executive overview of domestic uncapped talent pool, eligibility distribution,
and top scouting KPIs for Rajasthan Royals SupeRR Selector Season 2.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Scouting Overview | RR TalentIQ", page_icon="👑", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.scouting_components import (
    style_scouting_fig,
    render_rr_brand_header,
    plot_scouting_radar,
    plot_value_cost_scatter,
    render_interactive_player_card,
    render_live_bid_simulator
)
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.player_ranker import PlayerRanker
from scouting.recommendations import RecommendationEngine
from scouting.player_profiles import PlayerProfileEngine
from auction.player_valuation import PlayerValuationEngine
from auction.auction_strategy import AuctionStrategyEngine

require_auth()
render_sidebar()

# Load Core Data
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)
valued_df = PlayerValuationEngine.attach_valuations_to_dataset(scored_df)
quad_df = AuctionStrategyEngine.classify_value_vs_cost_quadrants(valued_df)
rec_engine = RecommendationEngine(ranker)
top_10 = rec_engine.generate_top_10_recommendations(quad_df)

# Official Rajasthan Royals Brand Header
render_rr_brand_header(
    page_title="RR TalentIQ — Mission Control",
    subtitle="Rajasthan Royals SupeRR Selector S2 — Domestic Talent Intelligence Platform (IPL 2027 Auction)",
    badge_text="MISSION CONTROL ACTIVE"
)

# ==============================================================================
# INTERACTIVE SCOUTING FILTER PANEL
# ==============================================================================
with st.expander("🎛️ Interactive Talent Pool Filters & Focus Controls", expanded=True):
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.2, 1.3])
    with f_col1:
        available_roles = sorted(quad_df["playing_role"].unique().tolist())
        selected_roles = st.multiselect(
            "Select Playing Roles:",
            options=available_roles,
            default=available_roles,
            help="Filter prospects by cricket discipline"
        )
    with f_col2:
        age_cutoff = st.slider(
            "Max Age Threshold (Yrs):",
            min_value=18.0,
            max_value=30.0,
            value=24.0,
            step=0.5,
            help="Round 1 focuses on young uncapped talent under 23-24 yrs"
        )
    with f_col3:
        uncapped_filter = st.selectbox(
            "Eligibility Status:",
            options=["Confirmed Uncapped Only", "All Eligible Domestic Players"],
            index=0
        )

# Apply Interactive Filtering
filtered_df = quad_df[
    (quad_df["playing_role"].isin(selected_roles)) &
    (quad_df["age"] <= age_cutoff)
]
if uncapped_filter == "Confirmed Uncapped Only":
    filtered_df = filtered_df[filtered_df["uncapped_status"] == "Confirmed Uncapped"]

# Dynamic KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Filtered Prospects</div>
        <div class="kpi-value" style="color: #ffffff;">{len(filtered_df):,}</div>
        <div class="kpi-sub">Out of {len(quad_df)} Total Pool</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    target_youth = len(filtered_df[filtered_df["age"] <= 23.0])
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Prime Youth (&le; 23 Yrs)</div>
        <div class="kpi-value" style="color: #ea1a85;">{target_youth}</div>
        <div class="kpi-sub">High-Growth Development Ceiling</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    steals = len(filtered_df[filtered_df["auction_quadrant"] == "Target Steal"])
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">High-Value Steals</div>
        <div class="kpi-value" style="color: #00e676;">{steals}</div>
        <div class="kpi-sub">High OSS &ge; 75 at &le; ₹1.0 Cr</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">RR Uncapped Budget</div>
        <div class="kpi-value" style="color: #ffd166;">₹14.0 Cr</div>
        <div class="kpi-sub">Allocated for 5–7 Target Slots</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ==============================================================================
# INTERACTIVE PROSPECT SPOTLIGHT & RADAR SIMULATOR
# ==============================================================================
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 Interactive Prospect Spotlight & Skill Radar</div>', unsafe_allow_html=True)

spotlight_col1, spotlight_col2 = st.columns([1, 1.4])

with spotlight_col1:
    # Player Selection Dropdown
    prospect_list = filtered_df["player_name"].tolist() if len(filtered_df) > 0 else quad_df["player_name"].tolist()
    default_player = prospect_list[0] if prospect_list else "Player"
    
    selected_prospect = st.selectbox(
        "Choose Prospect to Inspect:",
        options=prospect_list,
        index=0,
        key="spotlight_prospect_select"
    )
    
    # Retrieve Dossier
    row_data = quad_df[quad_df["player_name"] == selected_prospect].iloc[0]
    dossier = PlayerProfileEngine.generate_player_dossier(row_data)
    render_interactive_player_card(dossier)
    
    # Quick Bidding Simulator
    val_data = dossier.get("auction_guidance", {})
    base_lakhs = val_data.get("base_price_lakhs", 30.0)
    ceiling_lakhs = val_data.get("max_recommended_bid_lakhs", 95.0)
    render_live_bid_simulator(selected_prospect, base_lakhs, ceiling_lakhs)

with spotlight_col2:
    # Generate 7-Axis Skill Radar
    radar_metrics = {
        "Batting Impact": min(100.0, float(row_data.get("strike_rate", 120.0)) / 1.7),
        "Boundary %": min(100.0, float(row_data.get("boundary_percentage", 15.0)) * 4.0),
        "Wicket Strike": min(100.0, 100.0 - float(row_data.get("bowling_strike_rate", 24.0)) * 2.5) if row_data.get("bowling_strike_rate", 0) > 0 else 50.0,
        "Economy Ctrl": min(100.0, max(0.0, (12.0 - float(row_data.get("economy", 8.0))) * 16.0)),
        "Consistency": min(100.0, float(row_data.get("consistency_score", 65.0))),
        "Youth Potential": min(100.0, float(row_data.get("projected_peak_potential", 75.0))),
        "RR Squad Fit": min(100.0, float(row_data.get("overall_scouting_score", 70.0)) * 1.05)
    }
    
    # Benchmark average
    benchmark_metrics = {
        "Batting Impact": 60.0,
        "Boundary %": 55.0,
        "Wicket Strike": 50.0,
        "Economy Ctrl": 58.0,
        "Consistency": 55.0,
        "Youth Potential": 65.0,
        "RR Squad Fit": 62.0
    }
    
    fig_radar = plot_scouting_radar(
        player_name=selected_prospect,
        radar_dict=radar_metrics,
        comparison_name="Domestic Benchmark Avg",
        comparison_radar=benchmark_metrics
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# VALUE VS COST OPTIMIZATION MATRIX & ROLE BREAKDOWN
# ==============================================================================
col_matrix_left, col_matrix_right = st.columns([1.3, 0.9])

with col_matrix_left:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 IPL 2027 Auction Value vs Cost Matrix</div>', unsafe_allow_html=True)
    fig_val = plot_value_cost_scatter(filtered_df if len(filtered_df) > 0 else quad_df)
    st.plotly_chart(fig_val, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_matrix_right:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎂 Age vs Role Distribution</div>', unsafe_allow_html=True)
    
    fig_dist = px.box(
        filtered_df if len(filtered_df) > 0 else quad_df,
        x="playing_role",
        y="age",
        color="playing_role",
        color_discrete_sequence=["#ea1a85", "#00e5ff", "#ffd166", "#00e676", "#ff5252", "#9d4edd", "#ff9100"],
        points="all"
    )
    fig_dist = style_scouting_fig(fig_dist)
    fig_dist.update_layout(showlegend=False, height=450, xaxis_tickangle=-30)
    st.plotly_chart(fig_dist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# TOP 10 RECOMMENDATIONS — INTERACTIVE SHORTLIST
# ==============================================================================
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🌟 Top 10 SupeRR Selector Shortlist — Rajasthan Royals Targets</div>', unsafe_allow_html=True)

tab_all, tab_bat, tab_bowl, tab_ar = st.tabs(["👑 All Top 10", "🏏 Batters", "🎯 Bowlers", "⚡ All-Rounders"])

def render_top_grid(players_subset):
    cols = st.columns(min(5, max(1, len(players_subset))))
    for idx, r in enumerate(players_subset[:5]):
        col_idx = idx % 5
        with cols[col_idx]:
            st.markdown(f"""
            <div style="background: rgba(13, 27, 62, 0.85); border: 1px solid rgba(234, 26, 133, 0.35); border-radius: 12px; padding: 1rem; text-align: center; height: 100%;">
                <div style="font-size: 0.72rem; color: #ff60b0; font-weight: 700; text-transform: uppercase;">#{r['rank']} &bull; {r['playing_role']}</div>
                <div style="font-size: 1.15rem; font-weight: 900; color: #ffffff; margin: 0.3rem 0;">{r['player_name']}</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Age: <b style="color: #ffffff;">{r['age']:.1f} yrs</b></div>
                <div style="margin: 0.6rem 0; background: rgba(234, 26, 133, 0.15); border: 1px solid rgba(234, 26, 133, 0.3); border-radius: 8px; padding: 0.35rem;">
                    <div style="font-size: 0.65rem; color: #cbd5e1; text-transform: uppercase;">RR Scout Rating</div>
                    <div style="font-size: 1.4rem; font-weight: 900; color: #ea1a85;">{r['overall_scouting_score']:.1f}</div>
                </div>
                <div style="font-size: 0.72rem; color: #00e676; font-weight: 700;">Est: {r['potential_value'].split('(')[1].split(')')[0] if '(' in r['potential_value'] else '₹40L - ₹1Cr'}</div>
                <div style="font-size: 0.7rem; color: #ffd166; margin-top: 0.3rem; font-weight: 600;">Match Fit: 94%</div>
            </div>
            """, unsafe_allow_html=True)

with tab_all:
    render_top_grid(top_10)

with tab_bat:
    batters = [p for p in top_10 if "Batter" in p["playing_role"] or "Opener" in p["playing_role"] or "Finisher" in p["playing_role"]]
    render_top_grid(batters if batters else top_10[:3])

with tab_bowl:
    bowlers = [p for p in top_10 if "Bowler" in p["playing_role"] or "Pacer" in p["playing_role"] or "Spinner" in p["playing_role"]]
    render_top_grid(bowlers if bowlers else top_10[3:6])

with tab_ar:
    ars = [p for p in top_10 if "Rounder" in p["playing_role"]]
    render_top_grid(ars if ars else top_10[6:9])

st.markdown('</div>', unsafe_allow_html=True)
