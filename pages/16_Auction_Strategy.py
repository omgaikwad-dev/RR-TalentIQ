"""
RR TalentIQ - Rajasthan Royals Auction Strategy & War Room Simulator
Audits RR squad composition, roster priority gaps, estimated player market values,
and interactive Value-vs-Cost portfolio optimization for the IPL 2027 auction.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Auction Strategy | RR TalentIQ", page_icon="💰", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.scouting_components import render_rr_brand_header, style_scouting_fig, plot_value_cost_scatter
from analytics.domestic_data_loader import DomesticDataLoader
from scouting.player_ranker import PlayerRanker
from auction.rr_squad_analysis import RRSquadAnalyzer
from auction.squad_requirements import SquadRequirementsEngine
from auction.player_valuation import PlayerValuationEngine
from auction.auction_strategy import AuctionStrategyEngine

require_auth()
render_sidebar()

# Load Data & Valuation
loader = DomesticDataLoader()
raw_df = loader.load_unified_scouting_data(include_synthetic=False)
ranker = PlayerRanker()
scored_df = ranker.rank_players(raw_df)
valued_df = PlayerValuationEngine.attach_valuations_to_dataset(scored_df)
quad_df = AuctionStrategyEngine.classify_value_vs_cost_quadrants(valued_df)
budget_info = AuctionStrategyEngine.get_budget_overview()

render_rr_brand_header(
    page_title="Auction War Room & Valuation Intelligence",
    subtitle="Tactical squad requirement mapping, dynamic market valuations, and Value-vs-Cost portfolio optimization",
    badge_text="IPL 2027 AUCTION STRATEGY"
)

tab_matrix, tab_cart, tab_squad = st.tabs([
    "💰 Value vs Cost Strategy Matrix",
    "🛒 Interactive War Room & Target Cart",
    "🛡️ RR Squad Audit & Priority Gaps"
])

with tab_matrix:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 4-Quadrant Value vs Cost Optimization Matrix</div>', unsafe_allow_html=True)
    
    # Filter quadrant matrix by role
    all_q_roles = sorted(quad_df["playing_role"].unique().tolist())
    q_role_sel = st.multiselect("Filter Matrix by Role:", options=all_q_roles, default=all_q_roles, key="q_role_filter")
    sub_quad_df = quad_df[quad_df["playing_role"].isin(q_role_sel)]
    
    # Render interactive scatter plot
    fig_scatter = plot_value_cost_scatter(sub_quad_df)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Legend guide
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.75rem; margin-top: 0.5rem;">
        <div class="quadrant-pill quad-steal"><b>Quadrant 1 (Target Steals):</b> High OSS &ge; 75, Cost &le; &#8377;1.0 Cr</div>
        <div class="quadrant-pill quad-battle"><b>Quadrant 2 (Priority Battles):</b> High OSS &ge; 75, Cost > &#8377;1.0 Cr</div>
        <div class="quadrant-pill quad-depth"><b>Quadrant 3 (Squad Depth):</b> Mod OSS < 75, Cost &le; &#8377;1.0 Cr</div>
        <div class="quadrant-pill quad-avoid"><b>Quadrant 4 (High Risk / Avoid):</b> Mod OSS < 75, Cost > &#8377;1.0 Cr</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Master Valuation Table
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Estimated Market Value (EMV) & Max Recommended Bids</div>', unsafe_allow_html=True)
    
    disp_v_cols = [
        "player_name", "playing_role", "age",
        "overall_scouting_score", "estimated_market_value_lakhs",
        "max_recommended_bid_lakhs", "valuation_tier", "auction_quadrant"
    ]
    st.dataframe(
        quad_df[disp_v_cols].sort_values("overall_scouting_score", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with tab_cart:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛒 Interactive Auction Cart & Live Purse Simulator</div>', unsafe_allow_html=True)
    
    total_purse = 32.50 # Cr
    uncapped_cap = 14.0 # Cr
    
    # Interactive multi-select for target cart
    target_prospects = quad_df[quad_df["auction_quadrant"].isin(["Target Steal", "Priority Battle"])]["player_name"].tolist()
    default_cart = target_prospects[:3] if len(target_prospects) >= 3 else target_prospects
    
    selected_targets = st.multiselect(
        "Build Rajasthan Royals Target Auction Cart:",
        options=quad_df["player_name"].tolist(),
        default=default_cart,
        help="Select uncapped players to test purse impact and bid limits"
    )
    
    if selected_targets:
        cart_rows = quad_df[quad_df["player_name"].isin(selected_targets)].copy()
        
        # Interactive bid adjustment sliders per player
        st.markdown("<div style='font-size: 0.9rem; color: #ff60b0; font-weight: 700; margin: 0.8rem 0 0.4rem 0;'>⚡ Adjust Simulated Winning Bids:</div>", unsafe_allow_html=True)
        
        sim_bids = {}
        slider_cols = st.columns(min(3, len(cart_rows)))
        for idx, (_, r) in enumerate(cart_rows.iterrows()):
            c_idx = idx % 3
            with slider_cols[c_idx]:
                emv = float(r["estimated_market_value_lakhs"])
                max_b = float(r["max_recommended_bid_lakhs"])
                sim_bids[r["player_name"]] = st.slider(
                    f"{r['player_name']} (Lakhs):",
                    min_value=30.0,
                    max_value=max(150.0, max_b * 1.5),
                    value=emv,
                    step=5.0,
                    key=f"cart_slider_{r['player_name']}"
                )
                
        total_spent_lakhs = sum(sim_bids.values())
        total_spent_cr = total_spent_lakhs / 100.0
        remaining_total_purse = total_purse - total_spent_cr
        remaining_uncapped_purse = uncapped_cap - total_spent_cr
        
        # Live Purse Impact Dashboard
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Simulated Spend</div>
                <div class="kpi-value" style="color: #ea1a85;">₹{total_spent_cr:.2f} Cr</div>
                <div class="kpi-sub">{len(selected_targets)} Target Players Added</div>
            </div>
            """, unsafe_allow_html=True)
        with p_col2:
            rem_color = "#00e676" if remaining_uncapped_purse >= 0 else "#ff5252"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Uncapped Purse Left</div>
                <div class="kpi-value" style="color: {rem_color};">₹{remaining_uncapped_purse:.2f} Cr</div>
                <div class="kpi-sub">From ₹{uncapped_cap:.1f} Cr Target Limit</div>
            </div>
            """, unsafe_allow_html=True)
        with p_col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total RR Purse Left</div>
                <div class="kpi-value" style="color: #00e5ff;">₹{remaining_total_purse:.2f} Cr</div>
                <div class="kpi-sub">Total ₹{total_purse:.1f} Cr Auction Purse</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        # Summary Table
        cart_rows["Simulated Bid (₹ Lakhs)"] = cart_rows["player_name"].map(sim_bids)
        cart_rows["Bid Status"] = cart_rows.apply(
            lambda row: "✅ Value Buy" if row["Simulated Bid (₹ Lakhs)"] <= row["max_recommended_bid_lakhs"] else "⚠️ Overpay Alert",
            axis=1
        )
        display_cart = cart_rows[[
            "player_name", "playing_role", "age", "overall_scouting_score",
            "estimated_market_value_lakhs", "max_recommended_bid_lakhs",
            "Simulated Bid (₹ Lakhs)", "Bid Status"
        ]]
        st.dataframe(display_cart, use_container_width=True, hide_index=True)
    else:
        st.info("💡 Select one or more players above to simulate Rajasthan Royals' auction cart and purse remaining.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_squad:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛡️ Rajasthan Royals Squad Audit & Target Priorities</div>', unsafe_allow_html=True)
    
    sq_summary = RRSquadAnalyzer.get_squad_summary()
    gaps = RRSquadAnalyzer.identify_roster_gaps()
    
    col_s1, col_s2 = st.columns([1, 1.2])
    with col_s1:
        st.markdown(f"""
        <div style="background: rgba(13, 27, 62, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 1.2rem;">
            <div style="font-size: 1.1rem; font-weight: 800; color: #ffffff; margin-bottom: 0.8rem;">Current RR Roster Balance</div>
            <div style="line-height: 2; font-size: 0.9rem; color: #cbd5e1;">
                <div>Total Squad Size: <b style="color: #ffffff;">{sq_summary['total_players']} Players</b></div>
                <div>Overseas Slots Filled: <b style="color: #00e5ff;">{sq_summary['overseas_count']} / 8</b></div>
                <div>Indian Core: <b style="color: #ffffff;">{sq_summary['indian_count']} Players</b></div>
                <div>Total Purse Remaining: <b style="color: #00e676;">₹{budget_info['available_auction_purse_cr']} Cr</b></div>
                <div>Target Uncapped Allocation: <b style="color: #ffd166;">₹{budget_info['target_uncapped_allocation_cr']} Cr</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s2:
        st.markdown("""
        <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff; margin-bottom: 0.6rem;">Top 3 Tactical Deficits to Address:</div>
        """, unsafe_allow_html=True)
        for g in gaps:
            p_color = "#ea1a85" if g["priority"] == "CRITICAL" else ("#ffd166" if g["priority"] == "HIGH" else "#00e5ff")
            st.markdown(f"""
            <div style="background: rgba(13, 27, 62, 0.6); border-left: 4px solid {p_color}; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.6rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="color: #ffffff; font-size: 0.95rem;">{g['role']}</b>
                    <span style="color: {p_color}; font-weight: 800; font-size: 0.78rem;">{g['priority']} PRIORITY</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.2rem;">Target: {g['target_profile']}</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
