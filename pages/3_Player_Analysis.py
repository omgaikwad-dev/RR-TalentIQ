"""
IPL Analytics Pro - Player Analysis Page
Batting & bowling leaderboards, efficiency frontiers, batter-vs-bowler match-ups, and Virat Kohli deep dive.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Player Analysis | IPL Analytics Pro", page_icon="🏏", layout="wide")

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

from auth.authentication import require_auth
from components.sidebar import render_sidebar
from components.charts import (
    plot_top_run_scorers,
    plot_top_wicket_takers,
    plot_batting_scatter,
    style_fig
)
from analytics.data_loader import load_matches_data, load_deliveries_data
from analytics.player_analysis import PlayerAnalytics

require_auth()
render_sidebar()

matches_df = load_matches_data()
deliveries_df = load_deliveries_data()
pa = PlayerAnalytics(matches_df, deliveries_df)

st.markdown("""
<div class="main-header">
    <div>
        <h1>Player Performance Analytics</h1>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.3rem;">
            Batting titans, lethal bowling figures, efficiency frontiers, batter vs bowler match-ups, and legend deep dives
        </div>
    </div>
    <div>
        <span class="badge">INDIVIDUAL EXCELLENCE</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_leaders, tab_scatter, tab_trajectory, tab_matchup, tab_kohli = st.tabs([
    "👑 All-Time Leaderboards",
    "🎯 Efficiency Frontiers",
    "📈 Career Season Trajectory",
    "⚔️ Batter vs Bowler Matchup",
    "🐐 Virat Kohli Masterclass"
])

# Tab 1: All-Time Leaderboards
with tab_leaders:
    col_bat, col_bowl = st.columns(2)
    top_batters = pa.get_top_run_scorers(10)
    top_bowlers = pa.get_top_wicket_takers(10)
    
    with col_bat:
        st.plotly_chart(plot_top_run_scorers(top_batters), use_container_width=True)
    with col_bowl:
        st.plotly_chart(plot_top_wicket_takers(top_bowlers), use_container_width=True)
        
    st.markdown("### 📋 Top Run Scorers Table")
    st.dataframe(top_batters, use_container_width=True)
    
    csv_bat = top_batters.to_csv(index=True).encode("utf-8")
    st.download_button("📥 Download Batting Leaderboard (CSV)", data=csv_bat, file_name="ipl_top_batters.csv", mime="text/csv")
    
    st.write("")
    st.markdown("### 🎯 Leading Wicket-Takers Table")
    st.dataframe(top_bowlers, use_container_width=True)
    
    csv_bowl = top_bowlers.to_csv(index=True).encode("utf-8")
    st.download_button("📥 Download Bowling Leaderboard (CSV)", data=csv_bowl, file_name="ipl_top_bowlers.csv", mime="text/csv")

# Tab 2: Efficiency Frontiers
with tab_scatter:
    all_batters = pa.get_top_run_scorers(200)
    st.plotly_chart(plot_batting_scatter(all_batters), use_container_width=True)
    
    # Fours and Sixes breakdown of top 15 batters
    top_15_bat = pa.get_top_run_scorers(15)
    fig_bound = px.bar(
        top_15_bat,
        x="striker",
        y=["Fours", "Sixes"],
        barmode="group",
        color_discrete_sequence=["#48CAE4", "#FFB703"],
        labels={"value": "Count", "striker": "Batter", "variable": "Boundary Type"}
    )
    st.plotly_chart(style_fig(fig_bound, "Boundary Breakdown for Top 15 Run Scorers (4s vs 6s)"), use_container_width=True)

# Tab 3: Career Season Trajectory
with tab_trajectory:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Individual Player Career Progression</div>', unsafe_allow_html=True)
    
    popular_players = [
        "V Kohli", "RG Sharma", "MS Dhoni", "DA Warner", "AB de Villiers", 
        "SK Raina", "CH Gayle", "KL Rahul", "JJ Bumrah", "YS Chahal", "Rashid Khan"
    ]
    all_strikers = sorted(deliveries_df["striker"].unique().tolist())
    def_idx = all_strikers.index("V Kohli") if "V Kohli" in all_strikers else 0
    
    target_player = st.selectbox("Search or Select Player:", options=all_strikers, index=def_idx)
    traj_df = pa.get_player_season_trajectory(target_player)
    
    if len(traj_df) > 0:
        c1, c2 = st.columns(2)
        with c1:
            fig_traj_runs = px.bar(
                traj_df,
                x="Season",
                y="Runs",
                text="Runs",
                color="Strike Rate",
                color_continuous_scale="Viridis"
            )
            fig_traj_runs.update_traces(textposition="outside")
            st.plotly_chart(style_fig(fig_traj_runs, f"{target_player} — Annual Run Scoring Progression"), use_container_width=True)
            
        with c2:
            fig_traj_sr = px.line(
                traj_df,
                x="Season",
                y=["Average", "Strike Rate"],
                markers=True,
                color_discrete_sequence=["#06D6A0", "#FFB703"]
            )
            st.plotly_chart(style_fig(fig_traj_sr, f"{target_player} — Strike Rate & Average Progression"), use_container_width=True)
            
        st.dataframe(traj_df, use_container_width=True, hide_index=True)
    else:
        st.info("No records found for selected player.")
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 4: Batter vs Bowler Matchup
with tab_matchup:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚔️ Head-to-Head Batter vs Bowler Rivalry Simulator</div>', unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        strikers = sorted(deliveries_df["striker"].unique().tolist())
        sel_batter = st.selectbox("Select Batter:", options=strikers, index=strikers.index("V Kohli") if "V Kohli" in strikers else 0)
    with col_m2:
        bowlers = sorted(deliveries_df["bowler"].unique().tolist())
        sel_bowler = st.selectbox("Select Bowler:", options=bowlers, index=bowlers.index("JJ Bumrah") if "JJ Bumrah" in bowlers else 0)
        
    rivalry = pa.get_batter_vs_bowler(sel_batter, sel_bowler)
    
    if rivalry["balls"] == 0:
        st.warning(f"No recorded deliveries found between {sel_batter} and {sel_bowler} in regular IPL play.")
    else:
        r1, r2, r3, r4, r5 = st.columns(5)
        with r1:
            st.metric("Balls Faced", rivalry["balls"])
        with r2:
            st.metric("Runs Scored", rivalry["runs"])
        with r3:
            st.metric("Dismissals", rivalry["dismissals"])
        with r4:
            st.metric("Strike Rate", rivalry["strike_rate"])
        with r5:
            st.metric("Dot Ball %", f"{rivalry['dot_pct']}%")
            
        # Mini bar breakdown
        breakdown_df = pd.DataFrame([{
            "Dots": rivalry["dots"],
            "Fours (4s)": rivalry["fours"],
            "Sixes (6s)": rivalry["sixes"],
            "Dismissals": rivalry["dismissals"]
        }])
        fig_riv = px.bar(
            breakdown_df,
            barmode="group",
            color_discrete_sequence=["#94A3B8", "#48CAE4", "#FFB703", "#EF476F"]
        )
        st.plotly_chart(style_fig(fig_riv, f"Delivery Outcome Profile: {sel_batter} vs {sel_bowler}"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 5: Virat Kohli Masterclass
with tab_kohli:
    kohli = pa.get_virat_kohli_analysis()
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 183, 3, 0.15), rgba(11, 19, 43, 0.9)); border: 1px solid #ffb703; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #ffffff;">👑 {kohli['player']}</div>
                <div style="color: #ffb703; font-weight: 600; font-size: 0.95rem;">All-Time Highest Run Scorer in IPL History (Royal Challengers Bengaluru)</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2.2rem; font-weight: 800; color: #ffffff;">{kohli['total_runs']:,}</div>
                <div style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase;">Total IPL Career Runs</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Career Batting Average", kohli["batting_average"])
    with k2:
        st.metric("Career Strike Rate", kohli["strike_rate"])
    with k3:
        st.metric("Fours Struck", f"{kohli['fours']:,}")
    with k4:
        st.metric("Sixes Struck", f"{kohli['sixes']:,}")
        
    col_k_a, col_k_b = st.columns(2)
    with col_k_a:
        # Phase performance
        fig_phase = px.bar(
            kohli["phase_breakdown"],
            x="phase",
            y="Runs",
            color="Strike_Rate",
            text="Runs",
            color_continuous_scale="Plasma",
            labels={"phase": "Innings Phase"}
        )
        fig_phase.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig_phase, "Virat Kohli — Performance by Innings Phase"), use_container_width=True)
        
    with col_k_b:
        # Opponent performance
        fig_opp = px.bar(
            kohli["opponent_breakdown"].head(8),
            x="bowling_team",
            y="Runs",
            color="Strike_Rate",
            text="Runs",
            color_continuous_scale="Viridis",
            labels={"bowling_team": "Opponent Franchise"}
        )
        fig_opp.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig_opp, "Virat Kohli — Runs vs Major Franchises"), use_container_width=True)
