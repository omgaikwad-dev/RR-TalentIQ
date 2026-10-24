"""
IPL Analytics Pro - KPI Cards Component
Renders premium modern KPI cards with glassmorphism, accent borders, and dynamic metrics.
"""

import streamlit as st

def render_kpi_card(title: str, value: str, subtitle: str = None, icon: str = None):
    """Generates an individual styled KPI metric card."""
    icon_html = f"<span style='font-size: 1.1rem; margin-right: 0.4rem;'>{icon}</span>" if icon else ""
    sub_html = f"<div class='kpi-subtitle'>{subtitle}</div>" if subtitle else ""
    
    html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{icon_html}{title}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>
    """
    return html

def render_overview_kpis(kpis: dict):
    """Renders the top KPI row on the Overview dashboard."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_kpi_card(
            title="Total Matches",
            value=f"{kpis.get('total_matches', 0):,}",
            subtitle="2008–2026 Verified",
            icon="🏏"
        ), unsafe_allow_html=True)
        
    with col2:
        st.markdown(render_kpi_card(
            title="Seasons Covered",
            value=f"{kpis.get('seasons_count', 0)}",
            subtitle=f"Latest: Season {kpis.get('latest_season', 2026)}",
            icon="📅"
        ), unsafe_allow_html=True)
        
    with col3:
        st.markdown(render_kpi_card(
            title="Total Runs",
            value=f"{kpis.get('total_runs', 0):,}",
            subtitle=f"{kpis.get('total_sixes', 0):,} Sixes | {kpis.get('total_fours', 0):,} Fours",
            icon="🔥"
        ), unsafe_allow_html=True)
        
    with col4:
        st.markdown(render_kpi_card(
            title="Total Wickets",
            value=f"{kpis.get('total_wickets', 0):,}",
            subtitle=f"{kpis.get('total_deliveries', 0):,} Deliveries",
            icon="🎯"
        ), unsafe_allow_html=True)
        
    st.write("")
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown(render_kpi_card(
            title="Leading Run Scorer",
            value=kpis.get("top_run_scorer", "N/A"),
            subtitle=f"{kpis.get('top_runs', 0):,} Career Runs",
            icon="👑"
        ), unsafe_allow_html=True)
        
    with col6:
        st.markdown(render_kpi_card(
            title="Leading Wicket Taker",
            value=kpis.get("top_wicket_taker", "N/A"),
            subtitle=f"{kpis.get('top_wickets', 0)} Bowler Wickets",
            icon="⚡"
        ), unsafe_allow_html=True)
        
    with col7:
        st.markdown(render_kpi_card(
            title="Most Successful Team",
            value=kpis.get("top_team", "N/A"),
            subtitle=f"{kpis.get('top_team_wins', 0)} Match Victories",
            icon="🏆"
        ), unsafe_allow_html=True)
        
    with col8:
        st.markdown(render_kpi_card(
            title="Record Innings Total",
            value=str(kpis.get("record_innings_total", "287/3")),
            subtitle=kpis.get("record_innings_team", "Sunrisers Hyderabad"),
            icon="🚀"
        ), unsafe_allow_html=True)
