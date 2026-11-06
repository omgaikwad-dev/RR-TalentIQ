"""
RR TalentIQ - Official Rajasthan Royals Scouting Components
Interactive Plotly charts, radar diagrams, value-cost scatter plots,
glassmorphic talent cards, and auction bidding war simulator widgets.
"""

from typing import Dict, Any, List, Optional
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def style_scouting_fig(fig: go.Figure) -> go.Figure:
    """Applies authentic Rajasthan Royals deep midnight, royal pink, and cyan styling to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="#070d1e",
        plot_bgcolor="rgba(13, 27, 62, 0.45)",
        font=dict(color="#f8fafc", family="Segoe UI, system-ui, sans-serif"),
        title_font=dict(size=16, color="#ffffff", family="Segoe UI, sans-serif"),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            bgcolor="rgba(13, 27, 62, 0.75)",
            bordercolor="rgba(234, 26, 133, 0.3)",
            borderwidth=1,
            font=dict(color="#e2e8f0")
        ),
        hoverlabel=dict(
            bgcolor="#0d1b3e",
            font_size=12,
            font_family="Segoe UI, sans-serif",
            bordercolor="#ea1a85"
        )
    )
    fig.update_xaxes(
        gridcolor="rgba(0, 229, 255, 0.08)",
        zerolinecolor="rgba(234, 26, 133, 0.2)",
        title_font=dict(color="#94a3b8")
    )
    fig.update_yaxes(
        gridcolor="rgba(0, 229, 255, 0.08)",
        zerolinecolor="rgba(234, 26, 133, 0.2)",
        title_font=dict(color="#94a3b8")
    )
    return fig


def render_rr_brand_header(page_title: str, subtitle: str, badge_text: str = "IPL 2027 AUCTION INTELLIGENCE"):
    """Renders the official Rajasthan Royals hero banner with interactive visual cues."""
    st.markdown(f"""
    <div class="rr-hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.4rem;">
                    <span style="font-size: 1.8rem;">👑</span>
                    <span class="rr-tag-gold">RAJASTHAN ROYALS &bull; SUPER R SELECTOR S2</span>
                </div>
                <h1 class="rr-title-gradient">{page_title}</h1>
                <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem; max-width: 750px;">
                    {subtitle}
                </div>
            </div>
            <div style="text-align: right;">
                <span class="rr-badge">⚡ {badge_text}</span>
                <div style="font-size: 0.75rem; color: #ffd166; font-weight: 600; margin-top: 0.5rem;">
                    Available Purse: <span style="color: #00e676; font-weight: 800; font-size: 0.95rem;">₹32.50 Cr</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def plot_scouting_radar(
    player_name: str,
    radar_dict: Dict[str, float],
    comparison_name: Optional[str] = None,
    comparison_radar: Optional[Dict[str, float]] = None
) -> go.Figure:
    """
    Renders an interactive 7-dimensional radar chart.
    Styled with RR Royal Pink, Jaipur Gold concentric rings, and Cyan comparison.
    """
    categories = list(radar_dict.keys())
    values1 = list(radar_dict.values())
    categories_closed = categories + [categories[0]]
    values1_closed = values1 + [values1[0]]

    fig = go.Figure()

    # Primary Player Trace (RR Pink theme)
    fig.add_trace(go.Scatterpolar(
        r=values1_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(234, 26, 133, 0.28)",
        line=dict(color="#ea1a85", width=3),
        marker=dict(size=7, color="#ea1a85", symbol="circle"),
        name=f"<b>{player_name}</b>"
    ))

    # Optional Comparison Player Trace (Neon Cyan theme)
    if comparison_name and comparison_radar:
        values2 = [comparison_radar.get(cat, 50.0) for cat in categories]
        values2_closed = values2 + [values2[0]]
        fig.add_trace(go.Scatterpolar(
            r=values2_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(0, 229, 255, 0.2)",
            line=dict(color="#00e5ff", width=2.5, dash="dash"),
            marker=dict(size=6, color="#00e5ff", symbol="diamond"),
            name=f"<b>{comparison_name}</b>"
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(255, 209, 102, 0.15)",
                linecolor="rgba(234, 26, 133, 0.3)",
                tickfont=dict(color="#ffd166", size=9)
            ),
            angularaxis=dict(
                gridcolor="rgba(0, 229, 255, 0.15)",
                linecolor="rgba(255, 255, 255, 0.2)",
                tickfont=dict(color="#ffffff", size=11, family="Segoe UI")
            ),
            bgcolor="rgba(13, 27, 62, 0.6)"
        ),
        paper_bgcolor="#070d1e",
        font=dict(color="#f8fafc"),
        showlegend=True if comparison_name else False,
        margin=dict(l=40, r=40, t=30, b=30),
        height=400
    )
    return fig


def plot_value_cost_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Renders the 4-Quadrant Value vs Cost Auction Optimization chart.
    X-axis: Estimated Market Value (₹ Lakhs)
    Y-axis: Overall Scouting Score (0-100)
    """
    fig = px.scatter(
        df,
        x="estimated_market_value_lakhs",
        y="overall_scouting_score",
        color="playing_role",
        size="projected_peak_potential",
        hover_name="player_name",
        hover_data={
            "age": True,
            "playing_role": True,
            "estimated_market_value_lakhs": ":.1f",
            "overall_scouting_score": ":.1f",
            "projected_peak_potential": ":.1f",
            "auction_quadrant": True
        },
        title="IPL 2027 Auction Value vs Cost Strategy Matrix (Rajasthan Royals)",
        labels={
            "estimated_market_value_lakhs": "Estimated Market Value (₹ Lakhs)",
            "overall_scouting_score": "Overall Scouting Score (OSS)",
            "playing_role": "Playing Role"
        },
        color_discrete_sequence=["#ea1a85", "#00e5ff", "#ffd166", "#00e676", "#ff5252", "#9d4edd", "#ff9100"]
    )

    # Add quadrant divider lines at Cost = ₹100L, Score = 75.0
    fig.add_vline(x=100.0, line_width=1.5, line_dash="dash", line_color="rgba(234, 26, 133, 0.4)")
    fig.add_hline(y=75.0, line_width=1.5, line_dash="dash", line_color="rgba(0, 229, 255, 0.4)")

    # Quadrant Annotations
    fig.add_annotation(x=45, y=93, text="<b>QUADRANT 1: TARGET STEALS</b><br>(High Value, Low Cost)", showarrow=False, font=dict(color="#00e676", size=10))
    fig.add_annotation(x=180, y=93, text="<b>QUADRANT 2: PRIORITY WARS</b><br>(High Value, High Cost)", showarrow=False, font=dict(color="#ffd166", size=10))
    fig.add_annotation(x=45, y=55, text="<b>QUADRANT 3: SQUAD DEPTH</b><br>(Mod Value, Low Cost)", showarrow=False, font=dict(color="#00e5ff", size=10))
    fig.add_annotation(x=180, y=55, text="<b>QUADRANT 4: HIGH RISK AREA</b><br>(Mod Value, High Cost)", showarrow=False, font=dict(color="#ff5252", size=10))

    fig = style_scouting_fig(fig)
    fig.update_layout(height=520)
    return fig


def plot_pca_cluster_landscape(df: pd.DataFrame) -> go.Figure:
    """Renders 2D latent PCA space colored by K-Means cluster archetypes."""
    fig = px.scatter(
        df,
        x="pca_dim_1",
        y="pca_dim_2",
        color="cluster_archetype",
        hover_name="player_name",
        hover_data={
            "playing_role": True,
            "age": True,
            "overall_scouting_score": ":.1f",
            "strike_rate": ":.1f",
            "economy": ":.2f"
        },
        title="Unsupervised Player Archetype Landscape (PCA + K-Means)",
        labels={
            "pca_dim_1": "Principal Component 1 (Batting Intent & Power)",
            "pca_dim_2": "Principal Component 2 (Bowling Containment & Strike Wickets)",
            "cluster_archetype": "Archetype"
        },
        color_discrete_sequence=["#ea1a85", "#ffd166", "#00e5ff", "#00e676", "#9d4edd", "#ff5252"]
    )
    fig = style_scouting_fig(fig)
    fig.update_layout(height=480)
    return fig


def render_interactive_player_card(dossier: Dict[str, Any]):
    """Renders a high-interactivity Rajasthan Royals glassmorphic prospect card with expandable tabs."""
    oss = dossier.get("overall_scouting_score", 0.0)
    peak = dossier.get("projected_peak_potential", 0.0)
    role = dossier.get("playing_role", "Top-order Batter")
    age = dossier.get("age", 22.0)
    name = dossier.get("player_name", "Player")
    team = dossier.get("domestic_team", "State XI")
    strengths = dossier.get("strengths", [])
    top_strength = strengths[0] if strengths else "Consistent domestic execution"
    val_range = dossier.get("auction_guidance", {}).get("estimated_valuation_range", "₹40L - ₹1.0 Cr")

    st.markdown(f"""
    <div class="scouting-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
            <div>
                <span class="priority-tag">{role}</span>
                <span style="color: #94a3b8; font-size: 0.75rem; margin-left: 0.5rem;">{team}</span>
                <h3 style="color: #ffffff; margin: 0.3rem 0 0.1rem 0; font-size: 1.35rem; font-weight: 800;">{name}</h3>
                <div style="color: #ff60b0; font-size: 0.85rem; font-weight: 600;">Age: {age:.1f} yrs | {dossier.get('uncapped_status')}</div>
            </div>
            <div style="text-align: right;">
                <div style="background: rgba(234, 26, 133, 0.2); border: 1px solid #ea1a85; border-radius: 8px; padding: 0.35rem 0.75rem;">
                    <div style="font-size: 0.65rem; color: #cbd5e1; text-transform: uppercase;">RR Scout Rating</div>
                    <div style="font-size: 1.45rem; font-weight: 900; color: #ea1a85;">{oss:.1f}</div>
                </div>
                <div style="font-size: 0.72rem; color: #ffd166; margin-top: 0.3rem; font-weight: 600;">Est: {val_range}</div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 0.6rem; margin: 0.6rem 0; font-size: 0.8rem;">
            <div><span style="color: #94a3b8;">Peak Potential:</span> <b style="color: #00e5ff;">{peak:.1f}</b></div>
            <div><span style="color: #94a3b8;">Strike Rate:</span> <b style="color: #ffffff;">{dossier.get('strike_rate', 0.0):.1f}</b></div>
            <div><span style="color: #94a3b8;">Economy:</span> <b style="color: #ffffff;">{dossier.get('economy', 0.0):.2f}</b></div>
        </div>
        <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.4;">
            <b style="color: #00e676;">Key Asset:</b> {top_strength}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_live_bid_simulator(player_name: str, base_price_lakhs: float, max_ceiling_lakhs: float, current_rr_purse_cr: float = 32.5):
    """Interactive auction bidding war simulator widget right inside Streamlit."""
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">⚡ Interactive Auction War Room: {player_name}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        bid_input = st.slider(
            f"Simulate Auction Bidding (₹ Lakhs):",
            min_value=float(base_price_lakhs),
            max_value=float(max_ceiling_lakhs * 1.5),
            value=float(base_price_lakhs),
            step=5.0,
            key=f"bid_sim_{player_name}"
        )
    with col2:
        bid_cr = bid_input / 100.0
        remaining_purse = current_rr_purse_cr - bid_cr
        status_color = "#00e676" if bid_input <= max_ceiling_lakhs else "#ff5252"
        status_text = "WITHIN TARGET VALUE" if bid_input <= max_ceiling_lakhs else "OVERPAYMENT / WALK AWAY"
        st.markdown(f"""
        <div style="padding: 0.6rem; background: rgba(0,0,0,0.3); border-radius: 8px; text-align: center;">
            <div style="font-size: 0.72rem; color: #94a3b8;">DECISION STATUS</div>
            <div style="font-size: 0.95rem; font-weight: 800; color: {status_color};">{status_text}</div>
            <div style="font-size: 0.75rem; color: #cbd5e1; margin-top: 0.2rem;">Max Ceiling: ₹{max_ceiling_lakhs:.1f}L</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="padding: 0.6rem; background: rgba(0,0,0,0.3); border-radius: 8px; text-align: center;">
            <div style="font-size: 0.72rem; color: #94a3b8;">RR PURSE IMPACT</div>
            <div style="font-size: 1.15rem; font-weight: 900; color: #00e5ff;">₹{remaining_purse:.2f} Cr</div>
            <div style="font-size: 0.72rem; color: #cbd5e1;">From ₹{current_rr_purse_cr:.2f} Cr Total</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
