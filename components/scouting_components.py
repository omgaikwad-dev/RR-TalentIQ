"""
RR TalentIQ - Scouting Visualizations & Streamlit Components
Provides reusable interactive Plotly charts, radar diagrams, value-cost scatter plots,
PCA landscape visualizers, and glassmorphic talent cards.
"""

from typing import Dict, Any, List, Optional
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def style_scouting_fig(fig: go.Figure) -> go.Figure:
    """Applies Rajasthan Royals dark navy, blue, and pink styling to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="#0b132b",
        plot_bgcolor="rgba(28, 37, 65, 0.4)",
        font=dict(color="#f8fafc", family="Segoe UI, system-ui, sans-serif"),
        title_font=dict(size=16, color="#ffffff", family="Segoe UI, sans-serif"),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            bgcolor="rgba(28, 37, 65, 0.7)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1,
            font=dict(color="#e2e8f0")
        )
    )
    fig.update_xaxes(
        gridcolor="rgba(255, 255, 255, 0.08)",
        zerolinecolor="rgba(255, 255, 255, 0.15)",
        title_font=dict(color="#94a3b8")
    )
    fig.update_yaxes(
        gridcolor="rgba(255, 255, 255, 0.08)",
        zerolinecolor="rgba(255, 255, 255, 0.15)",
        title_font=dict(color="#94a3b8")
    )
    return fig


def plot_scouting_radar(
    player_name: str,
    radar_dict: Dict[str, float],
    comparison_name: Optional[str] = None,
    comparison_radar: Optional[Dict[str, float]] = None
) -> go.Figure:
    """
    Renders an interactive 7-dimensional radar chart.
    Supports single player inspection or head-to-head overlay.
    """
    categories = list(radar_dict.keys())
    values1 = list(radar_dict.values())
    # Close the polygon
    categories_closed = categories + [categories[0]]
    values1_closed = values1 + [values1[0]]

    fig = go.Figure()

    # Primary Player Trace (RR Pink theme)
    fig.add_trace(go.Scatterpolar(
        r=values1_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(255, 42, 133, 0.25)",
        line=dict(color="#ff2a85", width=2.5),
        name=player_name
    ))

    # Optional Comparison Player Trace (Cyan / Royal Blue theme)
    if comparison_name and comparison_radar:
        values2 = [comparison_radar.get(cat, 50.0) for cat in categories]
        values2_closed = values2 + [values2[0]]
        fig.add_trace(go.Scatterpolar(
            r=values2_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(0, 180, 216, 0.2)",
            line=dict(color="#00b4d8", width=2.5, dash="dash"),
            name=comparison_name
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(255, 255, 255, 0.12)",
                linecolor="rgba(255, 255, 255, 0.2)",
                tickfont=dict(color="#94a3b8", size=9)
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.12)",
                linecolor="rgba(255, 255, 255, 0.2)",
                tickfont=dict(color="#ffffff", size=11, family="Segoe UI")
            ),
            bgcolor="rgba(20, 30, 55, 0.5)"
        ),
        paper_bgcolor="#0b132b",
        font=dict(color="#f8fafc"),
        showlegend=True if comparison_name else False,
        margin=dict(l=40, r=40, t=30, b=30),
        height=380
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
        title="IPL 2027 Auction Value vs Cost Strategy Matrix",
        labels={
            "estimated_market_value_lakhs": "Estimated Market Value (₹ Lakhs)",
            "overall_scouting_score": "Overall Scouting Score (OSS)",
            "playing_role": "Role"
        },
        color_discrete_sequence=["#ff2a85", "#00b4d8", "#ffb703", "#2ec4b6", "#e76f51", "#9d4edd", "#52b788"]
    )

    # Add quadrant divider lines at Cost = ₹100L, Score = 75.0
    fig.add_vline(x=100.0, line_width=1.5, line_dash="dash", line_color="rgba(255, 255, 255, 0.3)")
    fig.add_hline(y=75.0, line_width=1.5, line_dash="dash", line_color="rgba(255, 255, 255, 0.3)")

    # Quadrant Annotations
    fig.add_annotation(x=45, y=92, text="<b>QUADRANT 1: TARGET STEALS</b><br>(High Value, Low Cost)", showarrow=False, font=dict(color="#2ecc71", size=10))
    fig.add_annotation(x=180, y=92, text="<b>QUADRANT 2: PRIORITY WARS</b><br>(High Value, High Cost)", showarrow=False, font=dict(color="#f39c12", size=10))
    fig.add_annotation(x=45, y=55, text="<b>QUADRANT 3: SQUAD DEPTH</b><br>(Mod Value, Low Cost)", showarrow=False, font=dict(color="#3498db", size=10))
    fig.add_annotation(x=180, y=55, text="<b>QUADRANT 4: HIGH RISK AREA</b><br>(Mod Value, High Cost)", showarrow=False, font=dict(color="#e74c3c", size=10))

    fig = style_scouting_fig(fig)
    fig.update_layout(height=520)
    return fig


def plot_pca_cluster_landscape(df: pd.DataFrame) -> go.Figure:
    """
    Renders 2D latent PCA space colored by K-Means cluster archetypes.
    """
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
            "pca_dim_1": "Principal Component 1 (Batting Power & Boundary Intent)",
            "pca_dim_2": "Principal Component 2 (Bowling Containment & Strike Wickets)",
            "cluster_archetype": "Discovered Archetype"
        },
        color_discrete_sequence=["#ff2a85", "#ffb703", "#00b4d8", "#2ec4b6", "#9d4edd", "#e76f51"]
    )
    fig = style_scouting_fig(fig)
    fig.update_layout(height=480)
    return fig


def render_player_spotlight_card(dossier: Dict[str, Any]):
    """Renders a rich glassmorphic talent spotlight card."""
    oss = dossier.get("overall_scouting_score", 0.0)
    peak = dossier.get("projected_peak_potential", 0.0)
    role = dossier.get("playing_role", "Top-order Batter")
    age = dossier.get("age", 22.0)
    name = dossier.get("player_name", "Player")
    team = dossier.get("domestic_team", "State XI")
    strengths = dossier.get("strengths", [])
    top_strength = strengths[0] if strengths else "Consistent domestic execution"

    st.markdown(f"""
    <div class="scouting-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
            <div>
                <span class="priority-tag">{role}</span>
                <span style="color: #94a3b8; font-size: 0.75rem; margin-left: 0.5rem;">{team}</span>
                <h3 style="color: #ffffff; margin: 0.3rem 0 0.1rem 0; font-size: 1.3rem;">{name}</h3>
                <div style="color: #ff75a0; font-size: 0.85rem; font-weight: 600;">Age: {age:.1f} yrs | {dossier.get('uncapped_status')}</div>
            </div>
            <div style="text-align: right;">
                <div style="background: rgba(255, 42, 133, 0.2); border: 1px solid #ff2a85; border-radius: 8px; padding: 0.35rem 0.65rem;">
                    <div style="font-size: 0.65rem; color: #cbd5e1; text-transform: uppercase;">Scout Rating</div>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #ff2a85;">{oss:.1f}</div>
                </div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; background: rgba(0,0,0,0.25); border-radius: 6px; padding: 0.5rem; margin: 0.6rem 0; font-size: 0.8rem;">
            <div><span style="color: #94a3b8;">Peak Potential:</span> <b style="color: #48cae4;">{peak:.1f}</b></div>
            <div><span style="color: #94a3b8;">Strike Rate:</span> <b style="color: #ffffff;">{dossier.get('strike_rate', 0.0):.1f}</b></div>
            <div><span style="color: #94a3b8;">Economy:</span> <b style="color: #ffffff;">{dossier.get('economy', 0.0):.2f}</b></div>
        </div>
        <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.4;">
            <b style="color: #2ecc71;">Key Asset:</b> {top_strength}
        </div>
    </div>
    """, unsafe_allow_html=True)

