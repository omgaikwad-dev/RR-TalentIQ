"""
IPL Analytics Pro - Global Filter Bar Component
Provides synchronized global filters for Season, Team, Venue, Result Type, and Toss Decision.
"""

import streamlit as st
import pandas as pd

def render_global_filters(matches_df: pd.DataFrame, key_prefix: str = "global"):
    """Renders a collapsible, cohesive filter bar and returns the selected filter criteria."""
    with st.expander("🔍 Global Analytics Filters & Search Parameters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        # Season filter
        all_seasons = sorted(matches_df["season"].dropna().unique().tolist())
        season_options = ["All Seasons (2008–2026)"] + [str(s) for s in all_seasons]
        
        with col1:
            selected_season_str = st.selectbox(
                "Season",
                options=season_options,
                index=0,
                key=f"{key_prefix}_season"
            )
            selected_season = None if "All" in selected_season_str else int(selected_season_str)
            
        # Team filter
        t1 = matches_df["team1"].dropna().unique()
        t2 = matches_df["team2"].dropna().unique()
        all_teams = sorted(list(set(t1) | set(t2)))
        team_options = ["All Teams"] + all_teams
        
        with col2:
            selected_team = st.selectbox(
                "Team",
                options=team_options,
                index=0,
                key=f"{key_prefix}_team"
            )
            selected_team = None if selected_team == "All Teams" else selected_team
            
        # Venue filter
        all_venues = sorted(matches_df["venue"].dropna().unique().tolist())
        venue_options = ["All Venues"] + all_venues
        
        with col3:
            selected_venue = st.selectbox(
                "Venue",
                options=venue_options,
                index=0,
                key=f"{key_prefix}_venue"
            )
            selected_venue = None if selected_venue == "All Venues" else selected_venue
            
        col4, col5, col6 = st.columns(3)
        
        with col4:
            result_opts = ["All Match Results", "Won by Runs (Defending)", "Won by Wickets (Chasing)", "Tied (Super Over)", "No Result"]
            selected_result = st.selectbox("Match Outcome", options=result_opts, index=0, key=f"{key_prefix}_result")
            result_map = {
                "Won by Runs (Defending)": "runs",
                "Won by Wickets (Chasing)": "wickets",
                "Tied (Super Over)": "tie_super_over",
                "No Result": "no_result"
            }
            res_val = result_map.get(selected_result, None)
            
        with col5:
            toss_opts = ["All Toss Decisions", "Chose to Bat First", "Chose to Field First"]
            selected_toss = st.selectbox("Toss Decision", options=toss_opts, index=0, key=f"{key_prefix}_toss")
            toss_map = {"Chose to Bat First": "bat", "Chose to Field First": "field"}
            toss_val = toss_map.get(selected_toss, None)
            
        with col6:
            st.write("")
            st.write("")
            reset_clicked = st.button("🔄 Reset All Filters", key=f"{key_prefix}_reset", use_container_width=True)
            if reset_clicked:
                for k in [f"{key_prefix}_season", f"{key_prefix}_team", f"{key_prefix}_venue", f"{key_prefix}_result", f"{key_prefix}_toss"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    return {
        "season": selected_season,
        "team": selected_team,
        "venue": selected_venue,
        "result_type": res_val,
        "toss_decision": toss_val
    }

def apply_match_filters(matches_df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Applies filter dictionary onto the matches DataFrame."""
    filtered = matches_df.copy()
    if filters.get("season"):
        filtered = filtered[filtered["season"] == filters["season"]]
    if filters.get("team"):
        t = filters["team"]
        filtered = filtered[(filtered["team1"] == t) | (filtered["team2"] == t)]
    if filters.get("venue"):
        filtered = filtered[filtered["venue"] == filters["venue"]]
    if filters.get("result_type"):
        filtered = filtered[filtered["result_type"] == filters["result_type"]]
    if filters.get("toss_decision"):
        filtered = filtered[filtered["toss_decision"] == filters["toss_decision"]]
    return filtered
