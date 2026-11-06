"""
RR TalentIQ - Player Comparison Engine & Battle Arena
Enables head-to-head multi-player comparison for up to 4 domestic players
with dual radar overlays, side-by-side metric tables, and strengths/weaknesses.
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Player Comparison | RR TalentIQ", page_icon="⚖️", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.scouting_components import render_rr_brand_header, plot_scouting_radar, style_scouting_fig
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.player_ranker import PlayerRanker
from scouting.player_profiles import PlayerProfileEngine
from auction.player_valuation import PlayerValuationEngine

require_auth()
render_sidebar()

# Load Data
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)
valued_df = PlayerValuationEngine.attach_valuations_to_dataset(scored_df)

render_rr_brand_header(
    page_title="Head-to-Head Battle Arena",
    subtitle="Compare domestic prospects across 7 radar skill dimensions, empirical metrics, and Rajasthan Royals tactical fit",
    badge_text="BATTLE ARENA BENCHMARK"
)

all_player_names = valued_df["player_name"].tolist()
default_selection = [all_player_names[0], all_player_names[1]] if len(all_player_names) >= 2 else all_player_names

# Interactive Selector Panel
with st.container():
    st.markdown('<div class="rr-filter-panel">', unsafe_allow_html=True)
    c_sel1, c_sel2 = st.columns([2.5, 1])
    with c_sel1:
        selected_players = st.multiselect(
            "Select 2 to 4 Players for Head-to-Head Comparison:",
            options=all_player_names,
            default=default_selection,
            max_selections=4
        )
    with c_sel2:
        radar_overlay_mode = st.radio("Radar Display:", ["Overlay (Side-by-Side)", "Individual Split"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

if len(selected_players) < 2:
    st.info("💡 Please select at least two players to generate comparative analytics.")
else:
    # Gather dossiers
    dossiers = []
    for p_name in selected_players:
        row = valued_df[valued_df["player_name"] == p_name].iloc[0]
        d = PlayerProfileEngine.generate_player_dossier(row)
        dossiers.append(d)

    # Top Row: Side-by-Side Glassmorphic Battle Cards
    kpi_cols = st.columns(len(dossiers))
    for idx, d in enumerate(dossiers):
        with kpi_cols[idx]:
            card_border = "#ea1a85" if idx == 0 else ("#00e5ff" if idx == 1 else "#ffd166")
            st.markdown(f"""
            <div class="scouting-card" style="border-color: {card_border};">
                <div style="font-size: 0.75rem; color: #ff60b0; font-weight: 700; text-transform: uppercase;">{d['playing_role']}</div>
                <div style="font-size: 1.3rem; font-weight: 900; color: #ffffff; margin: 0.2rem 0;">{d['player_name']}</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">{d['domestic_team']} &bull; Age: <b style="color: #ffffff;">{d['age']:.1f}</b></div>
                <div style="margin: 0.6rem 0; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 0.5rem; text-align: center;">
                    <div style="font-size: 0.65rem; color: #94a3b8; text-transform: uppercase;">RR Scout Rating</div>
                    <div style="font-size: 1.5rem; font-weight: 900; color: {card_border};">{d['overall_scouting_score']:.1f}</div>
                </div>
                <div style="font-size: 0.75rem; color: #cbd5e1; line-height: 1.4;">
                    <b style="color: #00e676;">Key Asset:</b> {d['strengths'][0] if d['strengths'] else 'Reliable domestic consistency'}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Interactive Radar Arena
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 7-Dimensional Skill Radar Battle</div>', unsafe_allow_html=True)

    def extract_radar(p_row):
        return {
            "Batting Impact": min(100.0, float(p_row.get("strike_rate", 120.0)) / 1.7),
            "Boundary %": min(100.0, float(p_row.get("boundary_percentage", 15.0)) * 4.0),
            "Wicket Strike": min(100.0, 100.0 - float(p_row.get("bowling_strike_rate", 24.0)) * 2.5) if p_row.get("bowling_strike_rate", 0) > 0 else 50.0,
            "Economy Ctrl": min(100.0, max(0.0, (12.0 - float(p_row.get("economy", 8.0))) * 16.0)),
            "Consistency": min(100.0, float(p_row.get("consistency_score", 65.0))),
            "Youth Potential": min(100.0, float(p_row.get("projected_peak_potential", 75.0))),
            "RR Squad Fit": min(100.0, float(p_row.get("overall_scouting_score", 70.0)) * 1.05)
        }

    if radar_overlay_mode == "Overlay (Side-by-Side)" and len(dossiers) >= 2:
        r1 = extract_radar(valued_df[valued_df["player_name"] == dossiers[0]["player_name"]].iloc[0])
        r2 = extract_radar(valued_df[valued_df["player_name"] == dossiers[1]["player_name"]].iloc[0])
        fig_dual = plot_scouting_radar(
            player_name=dossiers[0]["player_name"],
            radar_dict=r1,
            comparison_name=dossiers[1]["player_name"],
            comparison_radar=r2
        )
        st.plotly_chart(fig_dual, use_container_width=True)
    else:
        split_cols = st.columns(len(dossiers))
        for idx, d in enumerate(dossiers):
            with split_cols[idx]:
                r = extract_radar(valued_df[valued_df["player_name"] == d["player_name"]].iloc[0])
                fig_single = plot_scouting_radar(player_name=d["player_name"], radar_dict=r)
                st.plotly_chart(fig_single, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed Head-to-Head Comparison Matrix
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Direct Metric Breakdown & Stat Deltas</div>', unsafe_allow_html=True)

    metrics_list = [
        ("Playing Role", "playing_role"),
        ("Age (Years)", "age"),
        ("Uncapped Status", "uncapped_status"),
        ("Batting Strike Rate", "strike_rate"),
        ("Batting Average", "batting_average"),
        ("Boundary Percentage", "boundary_percentage"),
        ("Dot Ball % (Batting)", "dot_percentage"),
        ("Bowling Economy", "economy"),
        ("Bowling Strike Rate", "bowling_strike_rate"),
        ("Wickets", "wickets"),
        ("Consistency Score (0-100)", "consistency_score"),
        ("Projected Peak Potential", "projected_peak_potential"),
        ("Overall Scouting Score", "overall_scouting_score"),
        ("Estimated Market Value", "estimated_market_value_lakhs"),
        ("Max Recommended Bid", "max_recommended_bid_lakhs")
    ]

    table_data = []
    for label, field in metrics_list:
        row_entry = {"Metric Dimension": label}
        for d in dossiers:
            val = d.get(field, None)
            if val is None:
                # check row data
                r_item = valued_df[valued_df["player_name"] == d["player_name"]].iloc[0]
                val = r_item.get(field, "—")
            if isinstance(val, (int, float)):
                if "Rate" in label or "Percentage" in label or "Score" in label or "Potential" in label:
                    val = f"{val:.1f}"
                elif "Economy" in label:
                    val = f"{val:.2f}"
                elif "Value" in label or "Bid" in label:
                    val = f"₹{val:.1f} L"
                elif "Age" in label:
                    val = f"{val:.1f}"
            row_entry[d["player_name"]] = str(val)
        table_data.append(row_entry)

    comp_df = pd.DataFrame(table_data)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
