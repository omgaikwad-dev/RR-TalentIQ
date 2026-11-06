"""
RR TalentIQ - Rajasthan Royals Auction Strategy & Valuation Matrix
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
from components.scouting_components import style_scouting_fig, plot_value_cost_scatter
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

# Header
st.markdown("""
<div class="main-header">
    <div>
        <h1>RR Squad Analysis & Auction Intelligence</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Tactical squad requirement mapping, estimated valuations, and Value-vs-Cost portfolio optimization
        </div>
    </div>
    <div>
        <span class="rr-badge">IPL 2027 AUCTION STRATEGY</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_matrix, tab_squad, tab_cart = st.tabs(["💰 Value vs Cost Strategy Matrix", "🛡️ RR Squad Audit & Gaps", "🛒 Simulated Target Auction Cart"])

with tab_matrix:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 4-Quadrant Value vs Cost Optimization Matrix</div>', unsafe_allow_html=True)
    
    # Render interactive scatter plot
    fig_scatter = plot_value_cost_scatter(quad_df)
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

with tab_squad:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛡️ Rajasthan Royals Department Depth & Gap Severity</div>', unsafe_allow_html=True)
    
    depth_data = RRSquadAnalyzer.evaluate_department_depth()
    for dept_name, info in depth_data.items():
        st.markdown(f"""
        <div style="background: rgba(28, 37, 65, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 0.8rem; margin-bottom: 0.6rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 700; color: #ffffff; font-size: 1.05rem;">{dept_name}</div>
                <div>
                    <span style="background: rgba(255, 42, 133, 0.2); border: 1px solid #ff2a85; color: #ff75a0; font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 10px; font-weight: 700;">
                        Severity: {info['gap_severity']}
                    </span>
                    <span style="color: #48cae4; font-weight: 800; margin-left: 0.5rem;">{info['strength_rating']}/10</span>
                </div>
            </div>
            <div style="font-size: 0.82rem; color: #94a3b8; margin: 0.3rem 0;"><b>Key Personnel:</b> {', '.join(info['key_players'])}</div>
            <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.4;">{info['tactical_assessment']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Top 5 Tactical Targets
    st.markdown('<div class="section-title" style="margin-top: 1.2rem;">🎯 Top 5 Scouting Tactical Priorities for IPL 2027</div>', unsafe_allow_html=True)
    priority_matrix = SquadRequirementsEngine.get_priority_matrix()
    st.dataframe(priority_matrix, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_cart:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛒 Simulated Uncapped Domestic Auction Basket</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.8rem;">
        Budget Framework: <b>&#8377;{budget_info['target_uncapped_allocation_cr']:.1f} Cr</b> allocated for <b>{budget_info['recommended_uncapped_slots']}</b>.
        <br><i>Note: {budget_info['disclaimer']}</i>
    </div>
    """, unsafe_allow_html=True)

    target_cart = AuctionStrategyEngine.assemble_target_auction_cart(quad_df, budget_limit_lakhs=1400.0, max_picks=6)
    cart_df = pd.DataFrame(target_cart)
    
    st.dataframe(cart_df, use_container_width=True, hide_index=True)
    
    total_spent = sum(c["estimated_market_value_lakhs"] for c in target_cart) / 100.0
    st.markdown(f"""
    <div style="background: rgba(39, 174, 96, 0.15); border: 1px solid #27ae60; border-radius: 8px; padding: 0.8rem; margin-top: 0.8rem;">
        <b style="color: #2ecc71;">Basket Optimization Summary:</b> 
        Total Projected Spend: <b>&#8377;{total_spent:.2f} Cr</b> across {len(target_cart)} target picks.
        Remaining Reserve Buffer: <b>&#8377;{budget_info['target_uncapped_allocation_cr'] - total_spent:.2f} Cr</b>.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

