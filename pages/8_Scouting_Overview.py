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
from components.scouting_components import style_scouting_fig
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.player_ranker import PlayerRanker
from scouting.recommendations import RecommendationEngine
from auction.rr_squad_analysis import RRSquadAnalyzer

require_auth()
render_sidebar()

# Load Data
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)
rec_engine = RecommendationEngine(ranker)
top_10 = rec_engine.generate_top_10_recommendations(scored_df)

# Header
st.markdown("""
<div class="main-header">
    <div>
        <h1>RR TalentIQ — Scouting Overview</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Rajasthan Royals SupeRR Selector S2 — Domestic Talent Intelligence Platform (IPL 2027 Auction)
        </div>
    </div>
    <div>
        <span class="rr-badge">IPL 2027 AUCTION MISSION CONTROL</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Domestic Scouting Pool</div>
        <div class="kpi-value" style="color: #ffffff;">{len(scored_df):,}</div>
        <div class="kpi-sub">Verified Domestic Cricketers</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    uncapped_count = len(scored_df[scored_df["uncapped_status"] == "Confirmed Uncapped"])
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Confirmed Uncapped</div>
        <div class="kpi-value" style="color: #ff2a85;">{uncapped_count}</div>
        <div class="kpi-sub">0 International Senior Caps</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    young_count = len(scored_df[scored_df["age"] <= 23.0])
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Youth Assets (&le; 23.0 Yrs)</div>
        <div class="kpi-value" style="color: #48cae4;">{young_count}</div>
        <div class="kpi-sub">High-Growth Development Ceiling</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Target Uncapped Budget</div>
        <div class="kpi-value" style="color: #2ecc71;">&asymp; &#8377;14.0 Cr</div>
        <div class="kpi-sub">5 to 7 Domestic Target Slots</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Main View: Two Column Analysis
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Playing Role Distribution & Top Prospects</div>', unsafe_allow_html=True)
    
    role_counts = scored_df["playing_role"].value_counts().reset_index()
    role_counts.columns = ["Playing Role", "Player Count"]
    
    fig_role = px.bar(
        role_counts,
        x="Playing Role",
        y="Player Count",
        color="Playing Role",
        color_discrete_sequence=["#ff2a85", "#00b4d8", "#ffb703", "#2ec4b6", "#e76f51", "#9d4edd", "#52b788"],
        text="Player Count"
    )
    fig_role = style_scouting_fig(fig_role)
    fig_role.update_layout(showlegend=False, height=340, xaxis_tickangle=-25)
    st.plotly_chart(fig_role, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎂 Age Breakdown across Talent Pool</div>', unsafe_allow_html=True)
    
    fig_age = px.histogram(
        scored_df,
        x="age",
        nbins=12,
        color_discrete_sequence=["#00b4d8"],
        labels={"age": "Player Age (Years on 2027-01-01)", "count": "Cricketers Count"}
    )
    fig_age.add_vline(x=23.0, line_dash="dash", line_color="#ff2a85", annotation_text="Target Youth Cutoff (23.0)", annotation_position="top right")
    fig_age = style_scouting_fig(fig_age)
    fig_age.update_layout(height=340)
    st.plotly_chart(fig_age, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Top 5 Quick Glance Recommendations
st.markdown('<div class="content-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🌟 Top 5 SupeRR Selector Shortlist at a Glance</div>', unsafe_allow_html=True)

top_cols = st.columns(5)
for idx, r in enumerate(top_10[:5]):
    with top_cols[idx]:
        st.markdown(f"""
        <div style="background: rgba(28, 37, 65, 0.85); border: 1px solid rgba(255, 42, 133, 0.35); border-radius: 10px; padding: 0.9rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #ff75a0; font-weight: 700;">#{r['rank']} &bull; {r['playing_role']}</div>
            <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff; margin: 0.3rem 0;">{r['player_name']}</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Age: <b style="color: #ffffff;">{r['age']:.1f} yrs</b></div>
            <div style="margin-top: 0.5rem; background: rgba(255, 42, 133, 0.15); border-radius: 6px; padding: 0.25rem;">
                <span style="font-size: 0.7rem; color: #cbd5e1;">Scout Rating</span>
                <div style="font-size: 1.25rem; font-weight: 800; color: #ff2a85;">{r['overall_scouting_score']:.1f}</div>
            </div>
            <div style="font-size: 0.72rem; color: #2ecc71; margin-top: 0.4rem; font-weight: 600;">Est: {r['potential_value'].split('(')[1].split(')')[0] if '(' in r['potential_value'] else '₹40L - ₹1Cr'}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

