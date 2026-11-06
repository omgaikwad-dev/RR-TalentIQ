"""
RR TalentIQ — Rajasthan Royals Talent Intelligence System
Main Entry Point & Router for SupeRR Selector Season 2 Competition.
"""

import os
import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="RR TalentIQ — Rajasthan Royals Talent Intelligence System",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Styles
def load_custom_css():
    css_file = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

# Import Project Modules (Preserved for backward compatibility & testing)
from auth.authentication import (
    seed_demo_account,
    init_session_state,
    is_authenticated,
    login_session,
    authenticate_user,
    register_new_user,
    DEMO_USERNAME,
    DEMO_PASSWORD
)
from components.sidebar import render_sidebar
from components.kpi_cards import render_overview_kpis
from components.filters import render_global_filters, apply_match_filters
from components.charts import (
    plot_season_matches,
    plot_scoring_trends,
    plot_team_wins,
    plot_bat_first_vs_chasing,
    plot_toss_vs_match_win,
    plot_toss_decisions_by_season,
    plot_boundaries_trend
)
from analytics.data_loader import load_matches_data, load_deliveries_data
from analytics.season_analysis import SeasonAnalytics
from analytics.team_analysis import TeamAnalytics
from analytics.player_analysis import PlayerAnalytics
from analytics.match_insights import MatchInsights

# Seed Database and initialize default session
seed_demo_account()
init_session_state()

# Preserved Historical IPL Functions
def render_login_portal():
    """Renders the secure authentication gateway."""
    st.markdown("""
    <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">👑</div>
        <h1 style="color: #ffffff; font-size: 2.4rem; font-weight: 800; margin-bottom: 0.4rem;">
            RR TALENT<span style="color: #ff2a85;">IQ</span>
        </h1>
        <p style="color: #94a3b8; font-size: 1.05rem; max-width: 650px; margin: 0 auto;">
            Rajasthan Royals Talent Intelligence System | SupeRR Selector Season 2
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with tab_login:
            st.markdown("<div style='font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-bottom: 0.8rem;'>Analyst Sign In</div>", unsafe_allow_html=True)
            
            if "login_id" not in st.session_state:
                st.session_state["login_id"] = ""
            if "login_pwd" not in st.session_state:
                st.session_state["login_pwd"] = ""
                
            login_id = st.text_input("Username or Email", value=st.session_state["login_id"], placeholder="e.g. demo", key="input_login_id")
            login_pwd = st.text_input("Password", value=st.session_state["login_pwd"], type="password", placeholder="••••••••", key="input_login_pwd")
            
            if st.button("🚀 Access Analytics Dashboard", use_container_width=True, type="primary"):
                success, msg, user_info = authenticate_user(login_id, login_pwd)
                if success:
                    login_session(user_info)
                    st.success("✅ Authentication successful! Entering dashboard...")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
                    
            st.markdown(f"""
            <div class="demo-credentials-box">
                <div style="font-weight: 700; color: #ffb703; margin-bottom: 0.3rem;">⚡ Demo Account Credentials</div>
                <div><b>Username:</b> <code>{DEMO_USERNAME}</code></div>
                <div><b>Password:</b> <code>{DEMO_PASSWORD}</code></div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.3rem;">Pre-configured for evaluation & testing.</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✨ Quick Fill Demo Credentials", use_container_width=True):
                st.session_state["login_id"] = DEMO_USERNAME
                st.session_state["login_pwd"] = DEMO_PASSWORD
                st.rerun()

        with tab_signup:
            st.markdown("<div style='font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-bottom: 0.8rem;'>Register New Analyst</div>", unsafe_allow_html=True)
            new_user = st.text_input("Choose Username", placeholder="e.g., rahul_analyst", key="reg_username")
            new_email = st.text_input("Work or Personal Email", placeholder="e.g., rahul@example.com", key="reg_email")
            new_pwd = st.text_input("Password (min 6 chars)", type="password", placeholder="••••••••", key="reg_pwd")
            new_pwd_conf = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="reg_pwd_conf")
            
            if st.button("Register Account", use_container_width=True):
                ok, msg = register_new_user(new_user, new_email, new_pwd, new_pwd_conf)
                if ok:
                    st.success("🎉 Account created successfully! Please sign in with your credentials above.")
                else:
                    st.error(f"⚠️ {msg}")
                    
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("""
    <div style="text-align: center; margin-top: 2.5rem; color: #64748b; font-size: 0.8rem;">
        RR TalentIQ | Rajasthan Royals SupeRR Selector Season 2 | Cricsheet Verified Data
    </div>
    """, unsafe_allow_html=True)

def render_overview_dashboard():
    """Preserved historical overview intelligence dashboard."""
    matches_df = load_matches_data()
    deliveries_df = load_deliveries_data()
    
    sa = SeasonAnalytics(matches_df, deliveries_df)
    ta = TeamAnalytics(matches_df, deliveries_df)
    pa = PlayerAnalytics(matches_df, deliveries_df)
    mi = MatchInsights(matches_df, deliveries_df)
    
    st.markdown("""
    <div class="main-header">
        <div>
            <h1>IPL Analytics Pro</h1>
            <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
                Official Ball-by-Ball & Match Intelligence Dashboard (2008–2026)
            </div>
        </div>
        <div>
            <span class="badge">19 SEASONS VERIFIED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    top_bat = pa.get_top_run_scorers(1).iloc[0]
    top_bowl = pa.get_top_wicket_takers(1).iloc[0]
    top_team_row = ta.get_all_teams_summary().iloc[0]
    highest_inn = mi.get_highest_innings_totals(1).iloc[0]
    
    kpis = {
        "total_matches": len(matches_df),
        "seasons_count": matches_df["season"].nunique(),
        "latest_season": int(matches_df["season"].max()),
        "total_runs": int(deliveries_df["total_runs"].sum()),
        "total_deliveries": len(deliveries_df),
        "total_wickets": int(deliveries_df["is_wicket"].sum()),
        "total_fours": int(deliveries_df["is_boundary_four"].sum()),
        "total_sixes": int(deliveries_df["is_boundary_six"].sum()),
        "top_run_scorer": top_bat["striker"],
        "top_runs": int(top_bat["Runs"]),
        "top_wicket_taker": top_bowl["bowler"],
        "top_wickets": int(top_bowl["Wickets"]),
        "top_team": top_team_row["Team"],
        "top_team_wins": int(top_team_row["Won"]),
        "record_innings_total": f"{highest_inn['Score']}/{highest_inn['Wickets']}",
        "record_innings_team": highest_inn["batting_team"]
    }
    render_overview_kpis(kpis)
    
    filters = render_global_filters(matches_df, key_prefix="overview")
    filtered_matches = apply_match_filters(matches_df, filters)
    
    if len(filtered_matches) == 0:
        st.warning("⚠️ No matches match the selected filter combination.")
        return
        
    trends_df = sa.get_yearly_trends()
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_season_matches(trends_df), use_container_width=True)
    with col2:
        st.plotly_chart(plot_scoring_trends(trends_df), use_container_width=True)


# ==============================================================================
# RR TALENTIQ — STREAMLIT MULTIPAGE NAVIGATION ROUTER
# Renders only the 11 SupeRR Selector competition tabs in clean sidebar
# ==============================================================================
competition_pages = [
    st.Page("pages/8_Scouting_Overview.py", title="Scouting Overview", icon="👑", default=True),
    st.Page("pages/9_Player_Explorer.py", title="Player Explorer", icon="🔍"),
    st.Page("pages/10_Batting_Scouting.py", title="Batting Scouting", icon="🏏"),
    st.Page("pages/11_Bowling_Scouting.py", title="Bowling Scouting", icon="🎯"),
    st.Page("pages/12_All_Rounder_Analysis.py", title="All Rounder Analysis", icon="⚡"),
    st.Page("pages/13_Player_Comparison.py", title="Player Comparison", icon="⚖️"),
    st.Page("pages/14_Talent_Rankings.py", title="Talent Rankings", icon="🏆"),
    st.Page("pages/15_ML_Intelligence.py", title="ML Intelligence", icon="🤖"),
    st.Page("pages/16_Auction_Strategy.py", title="Auction Strategy", icon="💰"),
    st.Page("pages/17_Scouting_Reports.py", title="Scouting Reports", icon="📄"),
    st.Page("pages/6_Data_Quality.py", title="Data Quality", icon="🛡️"),
]

nav = st.navigation(competition_pages, position="sidebar", expanded=True)
nav.run()

